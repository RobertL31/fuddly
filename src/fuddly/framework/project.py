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

import queue as queue
import collections

from fuddly.framework.monitor import *
from fuddly.framework.knowledge.feedback_handler import *
from fuddly.framework.knowledge.information import InformationCollector
from fuddly.framework.value_types import VT
from fuddly.framework.node import Env
from fuddly.framework.data_model import DataModel
from fuddly.framework.tactics_helpers import DataMaker
from fuddly.framework.scenario import Scenario, ScenarioEnv

class Project(object):

    name = None
    default_dm = None

    wkspace_enabled = None
    wkspace_size = None
    wkspace_free_slot_ratio_when_full = None

    def __init__(self, enable_fbk_processing=True,
                 wkspace_enabled=True, wkspace_size=1000, wkspace_free_slot_ratio_when_full=0.5,
                 fmkdb_enabled=True,
                 default_fbk_timeout=None, default_fbk_mode=None,
                 default_sending_delay=None, default_burst_value=None,
                 samples_subdir='samples'):
        """

        Args:
            enable_fbk_processing: enable or disable the execution of feedback
              handlers, if any are set in the project.
            wkspace_enabled: If set to True, enable the framework workspace that store
              the generated data.
            wkspace_size: Maximum number of data that can be stored in the workspace.
            wkspace_free_slot_ratio_when_full: when the workspace is full, provide the ratio
              of the workspace size that will be used as the amount of entries to free in
              the workspace.
            fmkdb_enabled: If set to `True`, the fmkDB will be used. Otherwise, no DB transactions will
              occur and thus the fmkDB won't be filled during the session.
            default_fbk_timeout: If not None, when the project will be run, this value will be used
              to initialize the feedback timeout of all the targets
            default_fbk_mode: If not None, when the project will be run, this value will be used
              to initialize the feedback mode of all the targets
            default_sending_delay: If not None, when the project will be run, this value will be used
              to initialize the delay that is applied by the framework between each data sending.
            default_burst_value: If not None, when the project will be run, this value will be used
              to initialize the burst value of the framework (number of data that can be sent in burst
              before a delay is applied).
            samples_subdir: name of the directory from which to retrieve samples.
        """

        self.monitor = Monitor()
        self._knowledge_source = InformationCollector()
        self._fbk_processing_enabled = enable_fbk_processing
        self._feedback_processing_thread = None
        self._fbk_handlers = []
        self._fbk_handlers_disabled = False

        self.wkspace_enabled = wkspace_enabled
        self.wkspace_size = wkspace_size
        self.wkspace_free_slot_ratio_when_full = wkspace_free_slot_ratio_when_full
        self.fmkdb_enabled = fmkdb_enabled

        self.default_fbk_timeout = default_fbk_timeout
        self.default_fbk_mode = default_fbk_mode
        self.default_sending_delay = default_sending_delay
        self.default_burst_value = default_burst_value

        self.scenario_target_mapping = None
        self.reset_target_mappings()

        self._fmkops = None
        self.project_scenarios = None
        self.project_operators = None
        self.evol_processes = None
        self.targets = None
        self.dm = None
        self.directors = {}

        self._prj_fs_path = None
        self._samples_subdir = samples_subdir
        self._sample_files = None

    ################################
    ### Knowledge Infrastructure ###
    ################################

    @property
    def knowledge_source(self):
        return self._knowledge_source

    def add_knowledge(self, *info):
        self.knowledge_source.add_information(info, initial_trust_value=50)

    def reset_knowledge(self):
        self.knowledge_source.reset_information()

    def register_feedback_handler(self, fbk_handler):
        self._fbk_handlers.append(fbk_handler)

    def disable_feedback_handlers(self):
        self._fbk_handlers_disabled = True

    def enable_feedback_handlers(self):
        self._fbk_handlers_disabled = False

    def notify_data_sending(self, data_list, timestamp, target):
        if self._fbk_handlers_disabled:
            return

        for fh in self._fbk_handlers:
            fh.notify_data_sending(self.dm, data_list, timestamp, target)

    def trigger_feedback_handlers(self, source, timestamp, content, status):
        if not self._fbk_processing_enabled or self._fbk_handlers_disabled:
            return
        self._feedback_fifo.put((source, timestamp, content, status))

    def _feedback_processing(self):
        '''
        core function of the feedback processing thread
        '''
        while self._run_fbk_handling_thread:
            try:
                fbk_tuple = self._feedback_fifo.get(timeout=0.5)
            except queue.Empty:
                continue

            for fh in self._fbk_handlers:
                info = fh.process_feedback(self.dm, *fbk_tuple)
                if info:
                    self.knowledge_source.add_information(info)

    def estimate_last_data_impact_uniqueness(self):
        similarity = UNIQUE
        if self._fbk_processing_enabled:
            for fh in self._fbk_handlers:
                similarity += fh.estimate_last_data_impact_uniqueness()

        return similarity

    #####################
    ### Configuration ###
    #####################

    def set_logger(self, logger):
        self.logger = logger

    def set_targets(self, targets):
        self.targets = targets

    def set_monitor(self, monitor):
        self.monitor = monitor

    def set_data_model(self, dm):
        self.dm = dm

    def set_exportable_fmk_ops(self, fmkops):
        self._fmkops = fmkops

    def map_targets_to_scenario(self, scenario, target_mapping):
        if isinstance(scenario, (list, tuple)):
            for sc in scenario:
                name = sc.name if isinstance(sc, Scenario) else sc
                self.scenario_target_mapping[name] = target_mapping
        else:
            name = scenario.name if isinstance(scenario, Scenario) else scenario
            self.scenario_target_mapping[name] = target_mapping

    def reset_target_mappings(self):
        self.scenario_target_mapping = {}

    def register_scenarios(self, *scenarios):
        if self.project_scenarios is None:
            self.project_scenarios = []
        self.project_scenarios += scenarios

    def register_evolutionary_processes(self, *processes):
        if self.evol_processes is None:
            self.evol_processes = []
        self.evol_processes += processes

    def register_operators(self, *operators):
        if self.project_operators is None:
            self.project_operators = []
        self.project_operators += operators

    def register_director(self, name, obj):
        if name in self.directors:
            print("\n*** /!\\ ERROR: The director name '{:s}' is already used\n".format(name))
            raise ValueError

        self.directors[name] = obj

    def register_probe(self, probe, blocking=False):
        try:
            self.monitor.add_probe(probe, blocking)
        except AddExistingProbeToMonitorError as e:
            print("\n*** /!\\ ERROR: The probe name '{:s}' is already used\n".format(e.probe_name))
            raise ValueError

    ##########################
    ### Runtime Operations ###
    ##########################

    def share_knowlegde_source(self):
        VT.knowledge_source = self.knowledge_source
        Env.knowledge_source = self.knowledge_source
        DataModel.knowledge_source = self.knowledge_source
        DataMaker.knowledge_source = self.knowledge_source
        ScenarioEnv.knowledge_source = self.knowledge_source

    def start(self):
        for fh in self._fbk_handlers:
            fh.fmkops = self._fmkops
            fh._start(self.dm)

        if self._fbk_processing_enabled:
            self._run_fbk_handling_thread = True
            self._feedback_fifo = queue.Queue()
            self._feedback_processing_thread = threading.Thread(target=self._feedback_processing,
                                                                name='fuddly feedback processing')
            self._feedback_processing_thread.start()


    def stop(self):
        if self._fbk_processing_enabled:
            self._run_fbk_handling_thread = False
            if self._feedback_processing_thread:
                self._feedback_processing_thread.join()
            self._feedback_fifo = None

        for fh in self._fbk_handlers:
            fh._stop()

    def set_fs_path(self, prj_path):
        self._prj_fs_path = prj_path

    def get_sample_files(self, subdir):
        if self._prj_fs_path is None or self._samples_subdir is None or subdir is None:
            return None

        self._sample_files = collections.OrderedDict()
        samples_path = os.path.join(self._prj_fs_path, self._samples_subdir, subdir)
        if os.path.exists(samples_path):
            _, _, filenames = next(os.walk(samples_path))
            for f in filenames:
                self._sample_files[f] = os.path.join(samples_path, f)

        return self._sample_files

    def get_director(self, name):
        try:
            ret = self.directors[name]
        except KeyError:
            return None

        return ret

    def get_directors(self):
        return self.directors

    def get_probes(self):
        return self.monitor.get_probes_names()
