.. _gen:generic-generators:

Generic Data Makers
*******************

Generic Generators
==================

The current generic generators are presented within the following
sections.

GENP - Pattern Generation
-------------------------

Description:
  Generate basic data based on a pattern and different parameters.

Reference:
  :class:`fuddly.framework.generic_data_makers.g_generic_pattern`

Parameters:
    .. code-block:: none

        |_ pattern
        |      | desc: Pattern to be used for generating data
        |      | default: b'1234567890' [type: bytes]
        |_ prefix
        |      | desc: Prefix added to the pattern
        |      | default: b'' [type: bytes]
        |_ suffix
        |      | desc: Suffix replacing the end of the pattern
        |      | default: b'' [type: bytes]
        |_ size
        |      | desc: Size of the generated data.
        |      | default: None [type: int]
        |_ eval
        |      | desc: The pattern will be evaluated before being used. Note that the
        |      |       evaluation shall result in a byte string.
        |      | default: False [type: bool]


POPULATION - Generator for Evolutionary Fuzzing
-----------------------------------------------

This generator is used only internally by the evolutionary fuzzing infrastructure.


.. _dis:generic-operators:

Generic Operators
==================

The current generic operators are presented within the following
sections.

Stateful Operators
-------------------

.. _dis:ttype:

tTYPE - Advanced Alteration of Terminal Typed Node
++++++++++++++++++++++++++++++++++++++++++++++++++

Description:
  Perform alterations on typed nodes (one at a time) according to:

    - their type (e.g., INT, Strings, ...)
    - their attributes (e.g., allowed values, minimum size, ...)
    - knowledge retrieved from the data (e.g., if the input data uses separators, their symbols
      are leveraged in the fuzzing)
    - knowledge on the target retrieved from the project file or dynamically from feedback inspection
      (e.g., C language, GNU/Linux OS, ...)

  If the input has different shapes (described in non-terminal nodes), this will be taken into
  account by fuzzing every shape combinations.

  Note: this operator includes what tSEP does and goes beyond with respect to separators.

Reference:
  :class:`fuddly.framework.generic_data_makers.sd_fuzz_typed_nodes`

Parameters:
  .. code-block:: none

        |_ init
        |      | desc: make the model walker ignore all the steps until the provided
        |      |       one
        |      | default: 1 [type: int]
        |_ max_steps
        |      | desc: maximum number of steps (-1 means until the end)
        |      | default: -1 [type: int]
        |_ min_node_tc
        |      | desc: Minimum number of test cases per node (-1 means until the end)
        |      | default: -1 [type: int]
        |_ max_node_tc
        |      | desc: Maximum number of test cases per node (-1 means until the end).
        |      |       This value is used for nodes with a fuzz weight strictly greater
        |      |       than 1.
        |      | default: -1 [type: int]
        |_ clone_node
        |      | desc: if True, this operator will always return a copy of the node. (for
        |      |       stateless operators dealing with big data it can be useful
        |      |       to it to False)
        |      | default: True [type: bool]
        |_ path
        |      | desc: Graph path regexp to select nodes on which the operator should
        |      |       apply
        |      | default: None [type: str]
        |_ sem
        |      | desc: Semantics to select nodes on which the operator should apply.
        |      | default: None [type: str, list]
        |_ deep
        |      | desc: When set to True, if a node structure has changed, the modelwalker
        |      |       will reset its walk through the children nodes
        |      | default: True [type: bool]
        |_ full_combinatory
        |      | desc: When set to True, enable full-combinatory mode for non-terminal
        |      |       nodes. It means that the non-terminal nodes will be customized
        |      |       in "FullCombinatory" mode
        |      | default: False [type: bool]
        |_ ign_sep
        |      | desc: when set to True, separators will be ignored if
        |      |       any are defined.
        |      | default: False [type: bool]
        |_ fix
        |      | desc: limit constraints fixing to the nodes related to the currently
        |      |       fuzzed one (only implemented for 'sync_size_with' and
        |      |       'sync_enc_size_with')
        |      | default: True [type: bool]
        |_ fix_all
        |      | desc: for each produced data, reevaluate the constraints on the whole
        |      |       graph
        |      | default: False [type: bool]
        |_ order
        |      | desc: when set to True, the fuzzing order is strictly guided by the
        |      |       data structure. Otherwise, fuzz weight (if specified in the
        |      |       data model) is used for ordering
        |      | default: False [type: bool]
        |_ fuzz_mag
        |      | desc: order of magnitude for maximum size of some fuzzing test cases.
        |      | default: 1.0 [type: float]
        |_ make_determinist
        |      | desc: If set to 'True', the whole model will be set in determinist mode.
        |      |       Otherwise it will be guided by the data model determinism.
        |      | default: False [type: bool]
        |_ leaf_fuzz_determinism
        |      | desc: If set to 'True', each typed node will be fuzzed in a deterministic
        |      |       way. If set to 'False' each typed node will be fuzzed in a random
        |      |       way. Otherwise, if it is set to 'None', it will be guided by
        |      |       the data model determinism. Note: this option is complementary
        |      |       to 'determinism' as it acts on the typed node substitutions
        |      |       that occur through this operator
        |      | default: True [type: bool]
        |_ leaf_determinism
        |      | desc: If set to 'True', all the typed nodes of the model will be set
        |      |       to determinist mode prior to any fuzzing. If set to 'False',
        |      |       they will be set to random mode. Otherwise, if set to 'None',
        |      |       nothing will be done.
        |      | default: None [type: bool]
        |_ ign_mutable_attr
        |      | desc: Walk through all the nodes even if their Mutable attribute is
        |      |       cleared.
        |      | default: False [type: bool]
        |_ consider_sibbling_change
        |      | desc: While walking through terminal nodes, if sibbling nodes are
        |      |       no more the same because of existence condition for instance,
        |      |       walk through the new nodes.
        |      | default: True [type: bool]
        |_ csp_compliance_matters
        |      | desc: Does the compliance to any defined CSP should be always guaranteed?
        |      | default: False [type: bool]
        |_ only_corner_cases
        |      | desc: If set to True, when this operator walks through INT() and String()-based
        |      |       nodes, only valid corner cases will be generated
        |      | default: False [type: bool]
        |_ only_invalid_cases
        |      | desc: If set to True, when this operator walks through INT() and String()-based
        |      |       nodes, only invalid cases will be generated, meaning valid corner
        |      |       cases will not be generated.
        |      | default: False [type: bool]


tSTRUCT - Alter Data Structure
++++++++++++++++++++++++++++++

Description:
  Perform constraints alteration (one at a time) on each node that depends on another one
  regarding its existence, its quantity, its size, ...

  If `deep` is set, enable more corruption cases on the data structure, based on the internals of
  each non-terminal node:

    - the minimum and maximum amount of the sub-nodes of each non-terminal nodes
    - ...

Reference:
  :class:`fuddly.framework.generic_data_makers.sd_struct_constraints`

Parameters:
  .. code-block:: none

         |_ init
         |      | desc: make the model walker ignore all the steps until the provided
         |      |       one
         |      | default: 1 [type: int]
         |_ max_steps
         |      | desc: maximum number of steps (-1 means until the end)
         |      | default: -1 [type: int]
         |_ path
         |      | desc: graph path regexp to select nodes on which the operator should
         |      |       apply
         |      | default: None [type: str]
         |_ sem
         |      | desc: Semantics to select nodes on which the operator should apply.
         |      | default: None [type: str, list]
         |_ deep
         |      | desc: if True, enable corruption of non-terminal node internals
         |      | default: False [type: bool]

Usage Example:
   A typical *operator chain* for leveraging this operator could be:

   .. code-block:: none

      <Data Generator> tWALK(path='path/to/some/node') tSTRUCT

   .. note:: Test this chain with the data example found at
             :ref:`dm:pattern:existence-cond`, and set the path to the
             ``opcode`` node path.

   .. seealso:: Refer to :ref:`tuto:dmaker-chain` for insight
        into *operator chains*.



tALT - Walk Through Alternative Node Configurations
+++++++++++++++++++++++++++++++++++++++++++++++++++

Description:
  Switch the configuration of each node, one by one, with the provided
  alternate configuration.

Reference:
  :class:`fuddly.framework.generic_data_makers.sd_switch_to_alternate_conf`

Parameters:
  .. code-block:: none

         |_ clone_node
         |      | desc: if True, this operator will always return a copy of the node. (for
         |      |       stateless operators dealing with big data it can be useful
         |      |       to it to False)
         |      | default: True [type: bool]
         |_ init
         |      | desc: make the model walker ignore all the steps until the provided
         |      |       one
         |      | default: 1 [type: int]
         |_ max_steps
         |      | desc: maximum number of steps (-1 means until the end)
         |      | default: -1 [type: int]
         |_ min_node_tc
         |      | desc: Minimum number of test cases per node (-1 means until the end)
         |      | default: -1 [type: int]
         |_ max_node_tc
         |      | desc: Maximum number of test cases per node (-1 means until the end).
         |      |       This value is used for nodes with a fuzz weight strictly greater
         |      |       than 1.
         |      | default: -1 [type: int]
         |_ conf
         |      | desc: Change the configuration, with the one provided (by name), of
         |      |       all nodes reachable from the root, one-by-one. [default value
         |      |       is set dynamically with the first-found existing alternate configuration]
         |      | default: None [type: str, list, tuple]


tCONST - Alteration of Constraints
++++++++++++++++++++++++++++++++++

Description:
    When the CSP (Constraint Satisfiability Problem) backend are used in the node description.
    This operator negates the constraint one-by-one and output 1 or more samples for each negated
    constraint.

Reference:
  :class:`fuddly.framework.generic_data_makers.sd_constraint_fuzz`

Parameters:
  .. code-block:: none

    |_ const_idx
    |      | desc: Index of the constraint to begin with (first index is 1)
    |      | default: 1 [type: int]
    |_ sample_idx
    |      | desc: Index of the sample for the selected constraint to begin with
    |      |       (first index is 1)
    |      | default: 1 [type: int]
    |_ clone_node
    |      | desc: If True, this operator will always return a copy of the node.
    |      |       (for stateless diruptors dealing with big data it can be usefull
    |      |       to set it to False)
    |      | default: True [type: bool]
    |_ samples_per_cst
    |      | desc: Maximum number of samples to output for each negated constraint
    |      |       (-1 means until the end)
    |      | default: -1 [type: int]


tSEP - Alteration of Separator Node
+++++++++++++++++++++++++++++++++++

Description:
  Perform alterations on separators (one at a time). Each time a
  separator is encountered in the provided data, it will be replaced
  by another separator picked from the ones existing within the
  provided data.

Reference:
  :class:`fuddly.framework.generic_data_makers.sd_fuzz_separator_nodes`

Parameters:
  .. code-block:: none

         |_ clone_node
         |      | desc: if True, this operator will always return a copy of the node. (for
         |      |       stateless operators dealing with big data it can be useful
         |      |       to it to False)
         |      | default: True [type: bool]
         |_ init
         |      | desc: make the model walker ignore all the steps until the provided
         |      |       one
         |      | default: 1 [type: int]
         |_ max_steps
         |      | desc: maximum number of steps (-1 means until the end)
         |      | default: -1 [type: int]
         |_ min_node_tc
         |      | desc: Minimum number of test cases per node (-1 means until the end)
         |      | default: -1 [type: int]
         |_ max_node_tc
         |      | desc: Maximum number of test cases per node (-1 means until the end).
         |      |       This value is used for nodes with a fuzz weight strictly greater
         |      |       than 1.
         |      | default: -1 [type: int]
         |_ path
         |      | desc: graph path regexp to select nodes on which the operator should
         |      |       apply
         |      | default: None [type: str]
         |_ sem
         |      | desc: Semantics to select nodes on which the operator should apply.
         |      | default: None [type: str, list]
         |_ order
         |      | desc: when set to True, the fuzzing order is strictly guided by the
         |      |       data structure. Otherwise, fuzz weight (if specified in the
         |      |       data model) is used for ordering
         |      | default: False [type: bool]
         |_ deep
         |      | desc: when set to True, if a node structure has changed, the modelwalker
         |      |       will reset its walk through the children nodes
         |      | default: True [type: bool]



tWALK - Walk Through a Data Model
+++++++++++++++++++++++++++++++++

Description:
  Walk through the provided data and for each visited node, iterates
  over the allowed values (with respect to the data model).  Note: *no
  alteration* is performed by this operator.

Reference:
  :class:`fuddly.framework.generic_data_makers.sd_walk_data_model`

Parameters:
  .. code-block:: none

        |_ clone_node
        |      | desc: if True, this operator will always return a copy of the node. (for
        |      |       stateless operators dealing with big data it can be useful
        |      |       to it to False)
        |      | default: True [type: bool]
        |_ init
        |      | desc: make the model walker ignore all the steps until the provided
        |      |       one
        |      | default: 1 [type: int]
        |_ max_steps
        |      | desc: maximum number of steps (-1 means until the end)
        |      | default: -1 [type: int]
        |_ min_node_tc
        |      | desc: Minimum number of test cases per node (-1 means until the end)
        |      | default: -1 [type: int]
        |_ max_node_tc
        |      | desc: Maximum number of test cases per node (-1 means until the end).
        |      |       This value is used for nodes with a fuzz weight strictly greater
        |      |       than 1.
        |      | default: -1 [type: int]
        |_ path
        |      | desc: graph path regexp to select nodes on which the operator should
        |      |       apply
        |      | default: None [type: str]
        |_ sem
        |      | desc: Semantics to select nodes on which the operator should apply.
        |      | default: None [type: str, list]
        |_ full_combinatory
        |      | desc: When set to True, enable full-combinatory mode for non-terminal
        |      |       nodes. It means that the non-terminal nodes will be customized
        |      |       in "FullCombinatory" mode
        |      | default: True [type: bool]
        |_ leaf_determinism
        |      | desc: If set to 'True', all the typed nodes of the model will be set
        |      |       to determinist mode prior to any fuzzing. If set to 'False',
        |      |       they will be set to random mode. Otherwise, if set to 'None',
        |      |       nothing will be done.
        |      | default: None [type: bool]
        |_ order
        |      | desc: when set to True, the walking order is strictly guided by the
        |      |       data structure. Otherwise, fuzz weight (if specified in the
        |      |       data model) is used for ordering
        |      | default: True [type: bool]
        |_ nt_only
        |      | desc: Walk through non-terminal nodes only (taking into account recursive
        |      |       nodes).
        |      | default: False [type: bool]
        |_ walk_within_recursive_node
        |      | desc: Walk also within recursive nodes.
        |      | default: False [type: bool]
        |_ deep
        |      | desc: when set to True, if a node structure has changed, the modelwalker
        |      |       will reset its walk through the children nodes
        |      | default: True [type: bool]
        |_ fix_all
        |      | desc: for each produced data, reevaluate the constraints on the whole
        |      |       graph
        |      | default: True [type: bool]
        |_ ign_mutable_attr
        |      | desc: Walk through all the nodes even if their Mutable attribute is
        |      |       cleared.
        |      | default: True [type: bool]


tWALKcsp - Walk Through the Constraint of a Data Model
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Description:
    When the CSP (Constraint Satisfiability Problem) backend are used in the data description.
    This operator walk through the solutions of the CSP.

Reference:
  :class:`fuddly.framework.generic_data_makers.sd_walk_csp_solutions`

Parameters:
  .. code-block:: none

    |_ init
    |      | desc: Make the operator ignore all the steps until the provided one
    |      | default: 1 [type: int]
    |_ clone_node
    |      | desc: If True, this operator will always return a copy of the node.
    |      |       (for stateless diruptors dealing with big data it can be usefull
    |      |       to set it to False)
    |      | default: True [type: bool]
    |_ notify_exhaustion
    |      | desc: When all the solutions of the CSP have been walked through,
    |      |       the operator will notify it if this parameter is set to True.
    |      | default: True [type: bool]


Stateless Operators
--------------------

ADD - Add Data Within a Node
++++++++++++++++++++++++++++

Description:
   Add some data within the retrieved input.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_add_data`

Parameters:
  .. code-block:: none

        |_ path
        |      | desc: Graph path to select the node on which the operator should
        |      |       apply.
        |      | default: None [type: str]
        |_ after
        |      | desc: If True, the addition will be done after the selected node.
        |      |       Otherwise, it will be done before.
        |      | default: True [type: bool]
        |_ atom
        |      | desc: Name of the atom to add within the retrieved input. It is mutually
        |      |       exclusive with @raw
        |      | default: None [type: str]
        |_ raw
        |      | desc: Raw value to add within the retrieved input. It is mutually
        |      |       exclusive with @atom.
        |      | default: b'' [type: bytes, str]
        |_ name
        |      | desc: If provided, the added node will have this name.
        |      | default: None [type: str]


OP - Perform Operations on Nodes
++++++++++++++++++++++++++++++++

Description:
    Perform an operation on the nodes specified by the regexp path. @op is an operation that
    applies to a node and @params are a tuple containing the parameters that will be provided to
    @op. If no path is provided, the root node will be used.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_operate_on_nodes`

Parameters:
  .. code-block:: none

        |_ path
        |      | desc: Graph path regexp to select nodes on which the operator should
        |      |       apply.
        |      | default: None [type: str]
        |_ op
        |      | desc: The operation to perform on the selected nodes.
        |      | default: <function Node.clear_attr> [type: method, function]
        |_ op_ref
        |      | desc: Predefined operation that can be referenced by name. The current
        |      |       predefined function are: 'unfreeze', 'freeze', 'walk'. Take
        |      |       precedence over @op if not None.
        |      | default: None [type: str]
        |_ params
        |      | desc: Tuple of parameters that will be provided to the operation.
        |      | default: () [type: tuple]
        |_ clone_node
        |      | desc: If True the dmaker will always return a copy of the node. (For
        |      |       stateless operators dealing with big data it can be useful
        |      |       to set it to False.)
        |      | default: False [type: bool]


MOD - Modify Node Contents
++++++++++++++++++++++++++

Description:
    Perform modifications on the provided data. Two ways are possible:

    - Either the change is performed on the content of the nodes specified by the `path`
      parameter with the new `value` provided, and the optional constraints for the
      absorption (use *node absorption* infrastructure);

    - Or the changed is performed based on a dictionary provided through the parameter `multi_mod`

Reference:
  :class:`fuddly.framework.generic_data_makers.d_modify_nodes`

Parameters:
  .. code-block:: none

        |_ path
        |      | desc: Graph path regexp to select nodes on which the operator should
        |      |       apply.
        |      | default: None [type: str]
        |_ sem
        |      | desc: Semantics to select nodes on which the operator should apply.
        |      | default: None [type: str, list]
        |_ value
        |      | desc: The new value to inject within the data.
        |      | default: b'' [type: bytes]
        |_ constraints
        |      | desc: Constraints for the absorption of the new value.
        |      | default: AbsNoCsts() [type: AbsCsts]
        |_ multi_mod
        |      | desc: Dictionary of <path>:<item> pairs or <NodeSemanticsCriteria>:<item>
        |      |       pairs or <NodeInternalsCriteria>:<item> pairs to change multiple
        |      |       nodes with different values. <item> can be either only the new
        |      |       <value> or a tuple (<value>,<abscsts>) if new constraint for
        |      |       absorption is needed
        |      | default: None [type: dict]
        |_ unfold
        |      | desc: Resolve all the generator nodes within the input before performing
        |      |       the @path/@sem research
        |      | default: False [type: bool]
        |_ clone_node
        |      | desc: If True the dmaker will always return a copy of the node. (For
        |      |       stateless operators dealing with big data it can be useful
        |      |       to set it to False.)
        |      | default: False [type: bool]


CALL - Call Function
++++++++++++++++++++

Description:
    Call the function provided with the first parameter being the :class:`fuddly.framework.data.Data`
    object received as input of this operator, and optionally with additional parameters
    if `params` is set. The function should return a :class:`fuddly.framework.data.Data` object.

    The signature of the function should be compatible with:

    ``func(data, *args) --> Data()``

Reference:
  :class:`fuddly.framework.generic_data_makers.d_modify_nodes`

Parameters:
  .. code-block:: none

        |_ func
        |      | desc: The function that will be called with a node as its first parameter,
        |      |       and provided optionnaly with addtionnal parameters if @params
        |      |       is set.
        |      | default: lambda x: x [type: method, function]
        |_ params
        |      | desc: Tuple of parameters that will be provided to the function.
        |      | default: None [type: tuple]



NEXT - Next Node Content
++++++++++++++++++++++++

Description:
  Move to the next content of the nodes from input data or from only
  a piece of it (if the parameter `path` is provided). Basically,
  unfreeze the nodes then freeze them again, which will consequently
  produce a new data.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_next_node_content`

Parameters:
  .. code-block:: none

      |_ path
      |      | desc: graph path regexp to select nodes on which the operator should
      |      |       apply
      |      | default: None [type: str]
      |_ clone_node
      |      | desc: if True, this operator will always return a copy of the node. (for
      |      |       stateless operators dealing with big data it can be useful
      |      |       to it to False)
      |      | default: False [type: bool]
      |_ recursive
      |      | desc: apply the operator recursively
      |      | default: True [type: str]



FIX - Fix Data Constraints
++++++++++++++++++++++++++

Description:
  Release constraints from input data or from only a piece of it (if
  the parameter `path` is provided), then recompute them. By
  constraints we mean every generator (or function) nodes that may
  embeds constraints between nodes, and every node *existence
  conditions*.

  .. seealso:: Refer to :ref:`dm:pattern:existence-cond` for insight
           into existence conditions.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_fix_constraints`

Parameters:
  .. code-block:: none

      |_ path
      |      | desc: graph path regexp to select nodes on which the operator should
      |      |       apply
      |      | default: None [type: str]
      |_ clone_node
      |      | desc: if True, this operator will always return a copy of the node. (for
      |      |       stateless operators dealing with big data it can be useful
      |      |       to it to False)
      |      | default: False [type: bool]


ALT - Alternative Node Configuration
++++++++++++++++++++++++++++++++++++

Description:
  Switch to an alternate configuration.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_switch_to_alternate_conf`

Parameters:
  .. code-block:: none

         |_ path
         |      | desc: graph path regexp to select nodes on which the operator should
         |      |       apply
         |      | default: None [type: str]
         |_ recursive
         |      | desc: does the reachable nodes from the selected ones need also to
         |      |       be changed?
         |      | default: True [type: bool]
         |_ conf
         |      | desc: change the configuration, with the one provided (by name), of
         |      |       all subnodes fetched by @path, one-by-one. [default value is
         |      |       set dynamically with the first-found existing alternate configuration]
         |      | default: None [type: str]


C - Node Corruption
+++++++++++++++++++

Description:
  Corrupt bits on some nodes of the data model.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_corrupt_node_bits`

Parameters:
  .. code-block:: none

         |_ path
         |      | desc: graph path regexp to select nodes on which the operator should
         |      |       apply
         |      | default: None [type: str]
         |_ nb
         |      | desc: apply corruption on @nb Nodes fetched randomly within the data
         |      |       model
         |      | default: 2 [type: int]
         |_ ascii
         |      | desc: enforce all outputs to be ascii 7bits
         |      | default: False [type: bool]
         |_ new_val
         |      | desc: if provided change the selected byte with the new one
         |      | default: None [type: str]


Cp - Corruption at Specific Position
++++++++++++++++++++++++++++++++++++

Description:
  Corrupt bit at a specific byte.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_corrupt_bits_by_position`

Parameters:
  .. code-block:: none

         |_ new_val
         |      | desc: if provided change the selected byte with the new one
         |      | default: None [type: str]
         |_ ascii
         |      | desc: enforce all outputs to be ascii 7bits
         |      | default: False [type: bool]
         |_ idx
         |      | desc: byte index to be corrupted (from 1 to data length)
         |      | default: 1 [type: int]


EXT - Make Use of an External Program
+++++++++++++++++++++++++++++++++++++

Description:
  Call an external program to deal with the data.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_call_external_program`

Parameters:
  .. code-block:: none

         |_ path
         |      | desc: graph path regexp to select nodes on which the operator should
         |      |       apply
         |      | default: None [type: str]
         |_ cmd
         |      | desc: the command
         |      | default: None [type: list, tuple, str]
         |_ file_mode
         |      | desc: if True the data will be provided through a file to the external
         |      |       program, otherwise it will be provided on the command line directly
         |      | default: True [type: bool]


SIZE - Truncate
+++++++++++++++

Description:
  Truncate the data (or part of the data) to the provided size.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_max_size`

Parameters:
  .. code-block:: none

         |_ sz
         |      | desc: truncate the data (or part of the data) to the provided size
         |      | default: 10 [type: int]
         |_ path
         |      | desc: graph path regexp to select nodes on which the operator should
         |      |       apply
         |      | default: None [type: str]


STRUCT - Shake Up Data Structure
++++++++++++++++++++++++++++++++

Description:
  Alter the data model structure (replace ordered sections by
  unordered ones).

Reference:
  :class:`fuddly.framework.generic_data_makers.d_fuzz_model_structure`

Parameters:
  .. code-block:: none

         |_ path
         |      | desc: graph path regexp to select nodes on which the operator should
         |      |       apply
         |      | default: None [type: str]



COPY - Shallow Copy Data
++++++++++++++++++++++++

Description:
  Shallow copy of the input data, which means: ignore its frozen
  state during the copy.

Reference:
  :class:`fuddly.framework.generic_data_makers.d_shallow_copy`

.. note:: Random seeds are generally set while loading the data
          model. This operator enables you to reset the seeds for the
          input data.
