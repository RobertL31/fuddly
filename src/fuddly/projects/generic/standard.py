################################################################################
#
#  Copyright 2014-2016 Eric Lacombe <eric.lacombe@security-labs.org>
#
################################################################################
#
#  This file is part of fuddly.
#
#  fuddly is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  fuddly is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with fuddly. If not, see <http://www.gnu.org/licenses/>
#
################################################################################

import socket

from fuddly.framework.comm_backends import Shell_Backend
from fuddly.framework.plumbing import *
from fuddly.framework.targets.local import LocalTarget
from fuddly.framework.targets.network import NetworkTarget
from fuddly.framework.targets.printer import PrinterTarget

project = Project()
project.default_dm = ['mydf','jpg']
# If you only want one default DM, provide its name directly as follows:
# project.default_dm = 'mydf'

logger = Logger('standard', record_data=False, explicit_data_recording=True,
                enable_file_logging=False)

printer1_tg = PrinterTarget(tmpfile_ext='.png')
printer1_tg.set_target_ip('127.0.0.1')
printer1_tg.set_printer_name('PDF')

local_backend = Shell_Backend(timeout=2)
@blocking_probe(project)
class display_mem_check(ProbeMem):
    backend = local_backend
    process_name = 'display'
    tolerance = 10

local_tg = LocalTarget(tmpfile_ext='.png', target_path='/usr/bin/display')
local2_tg = LocalTarget(tmpfile_ext='.pdf', target_path='okular')
local3_tg = LocalTarget(tmpfile_ext='.zip', target_path='unzip', post_args='-d ' + gr.workspace_folder)
local4_tg = LocalTarget(target_path='python', pre_args='-c', send_via_cmdline=True)

net_tg = NetworkTarget(host='localhost', port=12345, data_semantics='TG1', hold_connection=True)
net_tg.register_new_interface('localhost', 54321, (socket.AF_INET, socket.SOCK_STREAM), 'TG2', server_mode=True)
net_tg.add_additional_feedback_interface('localhost', 7777, (socket.AF_INET, socket.SOCK_STREAM),
                                     fbk_id='My Feedback Source', server_mode=True)
net_tg.set_timeout(fbk_timeout=5, sending_delay=3)

netsrv_tg = NetworkTarget(host='localhost', port=12345, hold_connection=True, server_mode=True)

ETH_P_ALL = 3
rawnetsrv_tg = NetworkTarget(host='eth0', port=ETH_P_ALL,
                             socket_type=(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL)),
                             hold_connection=True, server_mode=False)

targets = [(local_tg, (display_mem_check, 0.1)),
           local2_tg,
           local3_tg,
           local4_tg,
           printer1_tg, net_tg, netsrv_tg, rawnetsrv_tg]


@director(project,
          args={'init': ('make the model walker ignore all the steps until the provided one', 1, int),
                'max_steps': ("number of test cases to run", 20, int),
                'mode': ('strategy mode (0 or 1)', 0, int),
                'path': ("path of the target application (for LocalTarget's only)", '/usr/bin/display', str)})
class Dir1(Director):

    def start(self, fmk_ops, dm, monitor, target, logger, user_input):

        if isinstance(target, LocalTarget):
            target.set_target_path(self.path)
            self._last_feedback = []

        self.nb_gen_val_cpt = 0
        if self.mode == 1:
            self.nb_gen_val_cpt = self.max_steps // 2
            self.max_steps = self.max_steps - self.nb_gen_val_cpt

        self.gen_ids = []
        for gid in fmk_ops.dynamic_generator_ids():
            self.gen_ids.append(gid)
        print('\n*** Data IDs found: ', self.gen_ids)
        self.init_gen_len = len(self.gen_ids)
        self.current_gen_id = self.gen_ids.pop(0)

        # fmk_ops.set_sending_delay(5)
        return True

    def stop(self, fmk_ops, dm, monitor, target, logger):
        if isinstance(target, LocalTarget):
            self._last_feedback = None

    def plan_next_instruction(self, fmk_ops, dm, monitor, target, logger, fmk_feedback):

        inst = Instruction()

        if self.max_steps > 0:
            
            if fmk_feedback.is_flag_set(FmkFeedback.NeedChange):
                try:
                    self.current_gen_id = self.gen_ids.pop(0)
                    inst.set_flag(Instruction.CleanupDMakers)
                except IndexError:
                    inst.set_flag(Instruction.Stop)
                    return inst

                change_list = fmk_feedback.get_flag_context(FmkFeedback.NeedChange)
                for dmaker, idx in change_list:
                    logger.log_fmk_info('Exhausted data maker [#{:d}]: {:s} ({:s})'.format(idx, dmaker['dmaker_type'], dmaker['dmaker_name']),
                                        nl_before=True, nl_after=False)

            clone_tag = "#{:d}".format(len(self.gen_ids) + 1)

            actions = [(self.current_gen_id + clone_tag, UI(finite=True)), ('tTYPE' + clone_tag, UI(init=self.init))]

            self.max_steps -= 1

        elif self.mode == 1 and self.nb_gen_val_cpt > 0:

            clone_tag2 = "#{:d}".format(self.init_gen_len + len(self.gen_ids) + 1)

            actions = [(self.current_gen_id + clone_tag2, UI(finite=True)), ('tALT' + clone_tag2, UI(init=self.init))]

            self.nb_gen_val_cpt -= 1

        else:
            actions = None

        if actions:
            inst.add_action(actions)
        else:
            inst.set_flag(Instruction.Stop)

        return inst


    def do_after_all(self, fmk_ops, dm, monitor, target, logger):
        linst = LastInstruction()

        if isinstance(target, LocalTarget):
            fbk = target.get_feedback()
            info = fbk.get_bytes()
            status_code = fbk.get_error_code()
            if status_code is not None and status_code < 0:
                linst.set_director_feedback('This input has crashed the target!')
                linst.set_director_status(-status_code) # does not prevent director to continue so
                                                        # provide a value > 0
            export = True
            if info in self._last_feedback:
                export = False
            elif info:
                self._last_feedback.append(info)
                linst.set_instruction(LastInstruction.RecordData)

        else:
            linst.set_instruction(LastInstruction.RecordData)
        
        return linst
