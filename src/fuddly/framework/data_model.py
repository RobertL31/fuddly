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

import threading

from fuddly.framework import global_resources as gr
from fuddly.framework.data import *
from fuddly.framework.dmhelpers.generic import *
from fuddly.framework.node_builder import NodeBuilder
from fuddly.libs.external_modules import *
from fuddly.libs.utils import Accumulator

import importlib

#### Data Model Abstraction

class DataModel(object):
    """
    Data Model Abstraction
    """

    file_extension = 'bin'
    name = None
    module_name = None

    knowledge_source = None

    def pre_build(self):
        """
        This method is called when a data model is loaded.
        It is executed before build_data_model().
        To be implemented by the user.
        """
        pass


    def build_data_model(self):
        """
        This method is called when a data model is loaded.
        It is called only the first time the data model is loaded.
        To be implemented by the user.
        """
        pass

    def validation_tests(self):
        """
        Optional test cases to validate the correct behavior of the data model

        Returns:
            bool: ``True`` if the validation succeeds. ``False`` otherwise

        """

        return True

    def _atom_absorption_additional_actions(self, atom):
        """
        Called by .create_atom_from_raw_data(). Should be overloaded if specific actions need to be
        performed on the atoms created from imported raw data

        Args:
            atom: Atom that are going to be registered after being absorbed from raw data

        Returns:
            An atom and a short description of the actions

        """
        return atom, ''


    def _create_atom_from_raw_data_specific(self, data, idx, filename):
        """
        Overload this method when creating a node from binary strings need more actions than
        performing a node absorption.

        Args:
            data (bytes): file content
            idx (int): index of the imported file
            filename (str): name of the imported file

        Returns:
            An atom or ``None``
        """
        raise NotImplementedError


    def create_atom_from_raw_data(self, data, idx, filename):
        """
        This function is called for each files (with the right extension)
        present in ``imported_data/<data_model_name>`` and absorb their content
        by leveraging the atoms of the data model registered for absorption or if none are
        registered, either call the method _create_atom_from_raw_data_specific() if it is defined or
        wrap their content in a :class:`framework.node.Node`.

        Args:
            data (bytes): file content
            idx (int): index of the imported file
            filename (str): name of the imported file

        Returns:
            An atom or ``None``

        """
        if self._default_atom_for_abs:
            atom, abs_csts = self._default_atom_for_abs
            nm = '{:s}_{:0>2d}'.format(self.name.upper(), idx)
            atom_for_abs = self._backend(atom).atom_copy(atom, new_name=nm)

            status, off, size, name = atom_for_abs.absorb(data, constraints=abs_csts)

            print('{:s} Absorb Status: {!r}, {:d}, {:d}'.format(nm, status, off, size))
            print(r' \_ length of original data: {:d}'.format(len(data)))
            print(r' \_ remaining: {!r}'.format(data[size:size+1000]))

            if status == AbsorbStatus.FullyAbsorbed:
                print("--> Create {:s} from files in '{:s}{:s}' directory"
                      .format(nm, gr.imported_data_folder, self.name))
                atom_for_abs, msg = self._atom_absorption_additional_actions(atom_for_abs)
                if msg:
                    print("     |_ {!s}".format(msg))
                return atom_for_abs
            else:
                return None
        else:
            try:
                return self._create_atom_from_raw_data_specific(data, idx, filename)
            except NotImplementedError:
                return Node('RAW_{:s}'.format(filename[:-len(self.file_extension) - 1]),
                            values=[data])

    def register_atom_for_decoding(self, atom, absorb_constraints=AbsFullCsts(),
                                   decoding_scope=None):
        """
        Register an atom that will be used by the DataModel when an operation requiring data absorption
        is performed, like self.decode().

        Args:
            atom: Atom to register for absorption
            absorb_constraints: Constraints to be used for the absorption
            decoding_scope: Should be either an atom name that can be
              absorbed by the registered atom, or a textual description of the scope, or
              a list of the previous elements.
              If set to None, the atom will be the default one
              used for decoding operation if no other nodes exist with a specific scope.

        """

        if self._atoms_for_abs is None:
            self._atoms_for_abs = {}
        atom_name, prepared_atom = self._backend(atom).prepare_atom(atom)
        if decoding_scope is None:
            decoding_scope = [atom_name]
            self._default_atom_for_abs = (prepared_atom, absorb_constraints)
        elif isinstance(decoding_scope, str):
            decoding_scope = [decoding_scope]

        assert isinstance(decoding_scope, (list, tuple))

        for scope in decoding_scope:
            self._atoms_for_abs[scope] = (prepared_atom, absorb_constraints)

    def decode(self, data, scope=None, atom_name=None, requested_abs_csts=None, colorized=True):
        """
        Args:
            data:
            atom_name (str): requested atom name for the decoding (linked to self.register_atom_for_decoding)
            scope (str): requested scope for the decoding (linked to self.register_atom_for_decoding)
            requested_abs_csts:
            colorized:

        Returns:
            tuple:
              Node which is the result of the absorption or None and
              Textual description of the result
        """

        a = Accumulator()
        accumulate = a.accumulate

        try:
            atom, extra = self.absorb(data, scope=scope, atom_name=atom_name, requested_abs_csts=requested_abs_csts)
        except ValueError as err:
            msg = colorize(f'\n*** ERROR: {err} ***', rgb=Color.ERROR)
            return None, msg

        status, off, size, name = extra

        if atom is None:
            accumulate(colorize("\n*** DECODING ERROR [atom used: '{:s}'] ***", rgb=Color.ERROR)
                       .format(name))
            accumulate('\nAbsorption Status: {!r}, {:d}, {:d}'.format(status, off, size))
            accumulate(r'\n \_ length of original data: {:d}'.format(len(data)))
            accumulate(r'\n \_ remaining: {!r}'.format(data[size:size+1000]))
        else:
            accumulate('\n')
            atom.show(log_func=accumulate, display_title=False, pretty_print=colorized)

        return atom, a.content

    def absorb(self, data, scope=None, atom_name=None, requested_abs_csts=None):
        """

        Args:
            data:
            atom_name (str): requested atom name for the decoding (linked to self.register_atom_for_decoding)
            scope (str): requested scope for the decoding (linked to self.register_atom_for_decoding)
            requested_abs_csts:

        Returns:
            Node:
              Node which is the result of the absorption or None
        """

        if scope is None and atom_name is None and self._default_atom_for_abs:
            atom, abs_csts = self._default_atom_for_abs
            atom_for_abs = self._backend(atom).atom_copy(atom)
            atom_name = atom.name
        elif scope is None and atom_name is None:
            atom_name = list(self._dm_hashtable.keys())[0]
            atom_for_abs = self.get_atom(atom_name)
            abs_csts = AbsFullCsts()
        else:
            try:
                if self._atoms_for_abs and scope in self._atoms_for_abs:
                    atom_for_abs, abs_csts = self.get_atom_for_absorption(scope)
                elif self._atoms_for_abs and atom_name in self._atoms_for_abs:
                    atom_for_abs, abs_csts = self.get_atom_for_absorption(atom_name)
                else:
                    atom_for_abs = self.get_atom(atom_name)
                    abs_csts = AbsFullCsts()
            except ValueError:
                raise ValueError(f"provided atom name is unknown: '{atom_name}'")

        abs_csts_to_apply = abs_csts if requested_abs_csts is None else requested_abs_csts
        status, off, size, name = atom_for_abs.absorb(data, constraints=abs_csts_to_apply)

        atom = atom_for_abs if status == AbsorbStatus.FullyAbsorbed else None

        return atom, (status, off, size, name)


    def cleanup(self):
        pass

    def __init__(self):
        self.node_backend = NodeBackend(self)
        self._dm_db = None
        self._built = False
        self._dm_hashtable = {}
        self._atoms_for_abs = None
        self._default_atom_for_abs= None
        self._decoded_data = None
        self._included_data_models = None
        self._dm_access_lock = threading.Lock()

    def _backend(self, atom):
        if isinstance(atom, (Node, dict)):
            return self.node_backend
        else:
            raise NotImplementedError

    def __str__(self):
        return self.name if self.name is not None else 'Unnamed'

    @property
    def included_models(self):
        return self._included_data_models

    def customize_node_backend(self, default_gen_custo=None, default_nonterm_custo=None):
        self.node_backend.default_gen_custo = default_gen_custo
        self.node_backend.default_nonterm_custo = default_nonterm_custo

    def register(self, *atom_list):
        for a in atom_list:
            if a is None: continue
            key, prepared_atom = self._backend(a).prepare_atom(a)
            self._dm_hashtable[key] = prepared_atom

    def get_atom(self, hash_key, name=None):
        with self._dm_access_lock:
            if hash_key in self._dm_hashtable:
                atom = self._dm_hashtable[hash_key]
                return self._backend(atom).atom_copy(atom, new_name=name)
            else:
                raise ValueError('Requested atom does not exist!')


    def get_atom_for_absorption(self, hash_key):
        if hash_key in self._atoms_for_abs:
            atom, abs_csts = self._atoms_for_abs[hash_key]
            return self._backend(atom).atom_copy(atom), abs_csts
        else:
            raise ValueError('Requested atom does not exist!')

    def get_external_atom(self, dm_name, data_id, name=None):
        dm = self._dm_db[dm_name]
        dm.load_data_model(self._dm_db)
        try:
            atom = dm.get_atom(data_id, name=name)
        except ValueError:
            return None

        return atom

    def load_data_model(self, dm_db):
        self.pre_build()
        if not self._built:
            self._dm_db = dm_db
            self.build_data_model()
            raw_data = self.import_file_contents(extension=self.file_extension)
            self.register(*list(map(lambda x: x[0], raw_data.values())))
            self._built = True

    def merge_with(self, data_model):
        if self._included_data_models is None:
            self._included_data_models = {}
        self._included_data_models[data_model] = []
        for k, v in data_model._dm_hashtable.items():
            if k in self._dm_hashtable:
                raise ValueError("the data ID {:s} exists already".format(k))
            else:
                self._dm_hashtable[k] = v
                self._included_data_models[data_model].append(k)

        self.node_backend.merge_with(data_model.node_backend)

    def atom_identifiers(self):
        hkeys = sorted(self._dm_hashtable.keys())
        for k in hkeys:
            yield k

    def update_atom(self, atom):
        self._backend(atom).update_atom(atom)

    def show(self):
        print(colorize(FontStyle.BOLD + '\n-=[ Data Types ]=-\n', rgb=Color.INFO))
        idx = 0
        for data_key in self._dm_hashtable:
            print(colorize('[%d] ' % idx + data_key, rgb=Color.SUBINFO))
            idx += 1

    def import_file_contents(self, extension=None, absorber=None,
                             subdir=None, path=None, filename=None):

        if absorber is None:
            absorber = self.create_atom_from_raw_data

        if extension is None:
            extension = self.file_extension
        if path is None:
            path = self.get_user_import_directory_path(subdir=subdir)

        files = {}

        # Get from packages (entry_points and fuddly)
        try:
            module_path = importlib.resources.files(self.module_name).joinpath("samples")
            _, _, filenames = next(os.walk(module_path))
            for f in filenames:
                files[f]=os.path.join(module_path, f)
        except StopIteration:
            # The folder doesn't exist
            pass

        # Imported data from the specified or default path (ususally the fuddly_data_folder)
        # This takes priority over all other files since it arrives last in the list
        _, _, filenames = next(os.walk(path))
        for f in filenames:
            files[f] = os.path.join(path, f)

        r_file = re.compile(r'.*\.' + extension + '$')
        def is_good_file_by_ext(info):
            return bool(r_file.match(info[0]))

        def is_good_file_by_fname(info):
            return filename == info[0]

        if filename is None:
            files = list(filter(is_good_file_by_ext, files.items()))
        else:
            files = list(filter(is_good_file_by_fname, files.items()))
        msgs = {}

        for (idx, (name, filepath)) in enumerate(files):
            with open(filepath, 'rb') as f:
                buff = f.read()
                d_abs = absorber(buff, idx, name)
                if d_abs is not None:
                    msgs[name] = (d_abs, filepath)

        return msgs

    def get_user_import_directory_path(self, subdir=None):
        if subdir is None:
            subdir = self.name
        if subdir is None:
            path = gr.imported_data_folder
        else:
            path = os.path.join(gr.imported_data_folder, subdir)

        if not os.path.exists(path):
            os.makedirs(path)

        return path

class NodeBackend(object):

    default_gen_custo = None
    default_nonterm_custo = None

    def __init__(self, data_model):
        self._dm = data_model
        self._confs = set()

    def merge_with(self, node_backend):
        self._confs = self._confs.union(node_backend._confs)

    def prepare_atom(self, atom):
        if not atom:
            msg = "\n*** WARNING: nothing to register for " \
                  "the data model '{nm:s}'!"\
                  "\n   [probable reason: {fdata:s}/imported_data/{nm:s}/ not " \
                  "populated with sample files]".format(nm=self._dm.name, fdata=gr.fuddly_data_folder)
            raise UserWarning(msg)

        if isinstance(atom, dict):
            mb = NodeBuilder(dm=self._dm, default_gen_custo=self.default_gen_custo,
                             default_nonterm_custo=self.default_nonterm_custo)
            desc_name = 'Unreadable Name'
            try:
                desc_name = atom['name']
                atom = mb.create_graph_from_desc(atom)
            except:
                print('-'*60)
                traceback.print_exc(file=sys.stdout)
                print('-'*60)
                msg = "*** ERROR: problem encountered with the '{desc!s}' descriptor!".format(desc=desc_name)
                raise UserWarning(msg)

        if atom.env is None:
            self.update_atom(atom)
        else:
            self.update_atom(atom, existing_env=True)

        self._confs = self._confs.union(atom.gather_alt_confs())

        return atom.name, atom

    def atom_copy(self, orig_atom, new_name=None):
        name = orig_atom.name if new_name is None else new_name
        node = Node(name, base_node=orig_atom, ignore_frozen_state=False, new_env=True)
        return node

    def update_atom(self, atom, existing_env=False):
        if not existing_env:
            atom.set_env(Env())
        atom.env.set_data_model(self._dm)

    def get_all_confs(self):
        return sorted(self._confs)
