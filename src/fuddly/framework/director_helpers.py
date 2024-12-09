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

from __future__ import print_function

import datetime

from fuddly.framework.global_resources import *
from fuddly.framework.tactics_helpers import _handle_user_inputs, _user_input_conformity, _restore_dmaker_internals

class Instruction(object):

    Stop = 1
    Exportable = 2
    CleanupDMakers = 3

    def __init__(self):
        self.action_register = []
        self.status = 0
        self.flags = {
            Instruction.Stop: False,
            Instruction.Exportable: False,
            Instruction.CleanupDMakers: False
            }

    def set_flag(self, name):
        if name not in self.flags:
            raise ValueError
        self.flags[name] = True

    def is_flag_set(self, name):
        if name not in self.flags:
            raise ValueError
        return self.flags[name]

    def set_status(self, status):
        self.status = status

    def add_action(self, actions, seed=None, tg_ids=None):
        l = list(actions) if actions is not None else None
        self.action_register.append((l, seed, tg_ids))

    def get_actions(self):
        return self.action_register


class LastInstruction(object):

    RecordData = 1

    def __init__(self):
        self._now = datetime.datetime.now()
        self.comments = None
        self.feedback_info = None
        self._status_code = 0
        self.instructions = {
            LastInstruction.RecordData: False
            }

    def set_instruction(self, name):
        if name not in self.instructions:
            raise ValueError
        self.instructions[name] = True

    def is_instruction_set(self, name):
        if name not in self.instructions:
            raise ValueError
        return self.instructions[name]

    def set_comments(self, comments):
        self.comments = comments

    def get_comments(self):
        return self.comments

    def set_director_status(self, status_code):
        self._status_code = status_code

    def get_director_status(self):
        return self._status_code

    def set_director_feedback(self, info):
        self.feedback_info = info

    def get_director_feedback(self):
        return self.feedback_info

    def get_timestamp(self):
        return self._now


class Director(object):

    _args_desc = None

    def __str__(self):
        return "Director '{:s}'".format(self.__class__.__name__)

    def start(self, fmk_ops, dm, monitor, target, logger, user_input):
        '''
        To be overloaded if specific initialization code is needed.
        Shall return True if setup has succeeded, otherwise shall
        return False.
        '''
        return True

    def stop(self, fmk_ops, dm, monitor, target, logger):
        '''
        To be overloaded if specific termination code is needed.
        '''
        pass

    def plan_next_instruction(self, fmk_ops, dm, monitor, target, logger, fmk_feedback):
        '''
        Shall return an Instruction object that contains the actions
        that you want fuddly to perform.

        Returns:
          Instruction: Actions you want fuddly to perform.
        '''
        raise NotImplementedError('Directors shall implement this method!')

    def do_after_all(self, fmk_ops, dm, monitor, target, logger):
        '''
        This action is executed after data has been sent to the target
        AND that all blocking probes have returned.
        BUT just before data is logged.

        Returns:
          LastInstruction: Last-minute instructions you request fuddly
            to perform.
        '''

        linst = LastInstruction()

        # In order to export data in
        # any case, that is even if the Logger has been set to
        # export data only when requested (i.e. explicit_export == True)
        linst.set_instruction(LastInstruction.RecordData)

        return linst

    def _start(self, fmk_ops, dm, monitor, target, logger, user_input):
        # sys.stdout.write("\n__ setup director '%s' __" % self.__class__.__name__)
        if not _user_input_conformity(self, user_input, self._args_desc):
            return False

        _handle_user_inputs(self, user_input)
        try:
            ok = self.start(fmk_ops, dm, monitor, target, logger, user_input)
        except:
            ok = False
            raise
        finally:
            if not ok:
                _restore_dmaker_internals(self)

        return ok


def director(prj, args=None):
    def internal_func(director_cls):
        director_cls._args_desc = {} if args is None else args
        if args is not None:
            # create specific attributes
            for k, v in args.items():
                desc, default, arg_type = v
                setattr(director_cls, k, default)
        # register an object of this class
        director = director_cls()
        prj.register_director(director.__class__.__name__, director)
        return director_cls

    return internal_func
