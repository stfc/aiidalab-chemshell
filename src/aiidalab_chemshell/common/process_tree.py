"""
Extend ``aiidalab-widgets-base``'s process node tree to also show inputs.

``aiidalab_widgets_base.ProcessNodesTreeWidget`` builds a tree of nodes linked
to a process via its outputs (``CREATE``/``RETURN`` links) and its called
sub-processes (``CALL_CALC``/``CALL_WORK`` links), but never shows the nodes
that were fed *into* the process (``INPUT_CALC``/``INPUT_WORK`` links, e.g.
the input structure or QM parameters). This module adds an "inputs" branch
alongside the existing "outputs" branch by subclassing a handful of
non-public ``aiidalab_widgets_base.nodes``/``process`` classes.

This is intentionally scoped to ``aiidalab-chemshell`` for now. Once it has
been tested and user-verified it is intended to be lifted into
``alc-aiidalab-widgets`` (as a reusable, exported widget) so other
ALC-maintained AiiDAlab apps can use it too.

Warnings
--------
This relies on subclassing several non-public, undocumented internal classes
of ``aiidalab-widgets-base`` (``NodesTreeWidget``, ``AiidaProcessNodeTreeNode``,
``AiidaOutputsTreeNode`` and the per-node-type process tree-node classes).
Behaviour has been verified against ``aiidalab-widgets-base`` 2.5.1 and 3.0.1
(the latter matching this project's pinned dependency range); re-verify
against the installed version after any upgrade of that pin.
"""

import functools

import ipywidgets as ipw
from aiida import common, orm
from aiidalab_widgets_base.nodes import (
    AiidaOutputsTreeNode,
    AiidaProcessNodeTreeNode,
    CalcFunctionTreeNode,
    CalcJobTreeNode,
    NodesTreeWidget,
    WorkChainProcessTreeNode,
)
from aiidalab_widgets_base.process import (
    ProcessNodesTreeWidget as AiiDAlabProcessNodesTreeWidget,
)
from traitlets import Unicode


class AiidaInputsTreeNode(AiidaOutputsTreeNode):
    """
    Tree node representing the "inputs" folder of a process node.

    Subclasses :class:`~aiidalab_widgets_base.nodes.AiidaOutputsTreeNode`
    (rather than introducing a wholly new base class) so that the upstream
    ``isinstance(node, AiidaOutputsTreeNode)`` checks in
    ``NodesTreeWidget._observe_tree_selected_nodes`` and
    ``NodesTreeWidget.find_node`` - which resolve such nodes via their
    ``parent_pk`` rather than a ``pk`` of their own - also apply correctly to
    this "inputs" folder without requiring any further overrides.
    """

    icon = Unicode("sign-in").tag(sync=True)


class _TreeNodeWithInputsMixin:
    """Mixin that attaches an ``inputs_node`` folder to a process tree node."""

    def __init__(self, pk, **kwargs):
        """
        Construct the tree node and attach a sibling "inputs" folder.

        Mirrors how ``AiidaProcessNodeTreeNode.__init__`` eagerly builds its
        own ``outputs_node`` attribute.

        Parameters
        ----------
        pk : int
            Primary key of the underlying AiiDA process node.
        **kwargs
            Forwarded to the next class in the MRO.
        """
        super().__init__(pk=pk, **kwargs)
        self.inputs_node = AiidaInputsTreeNode(name="inputs", parent_pk=pk)


class WorkChainProcessTreeNodeWithInputs(
    _TreeNodeWithInputsMixin, WorkChainProcessTreeNode
):
    """``WorkChainProcessTreeNode`` variant that also exposes process inputs."""


class CalcJobTreeNodeWithInputs(_TreeNodeWithInputsMixin, CalcJobTreeNode):
    """``CalcJobTreeNode`` variant that also exposes process inputs."""


class CalcFunctionTreeNodeWithInputs(_TreeNodeWithInputsMixin, CalcFunctionTreeNode):
    """``CalcFunctionTreeNode`` variant that also exposes process inputs."""


class NodesTreeWidgetWithInputs(NodesTreeWidget):
    """
    ``NodesTreeWidget`` variant that also shows nodes linked via input links.

    Overrides :attr:`NODE_TYPE` so every process/sub-process tree node gains
    an ``inputs_node`` folder (mirroring the existing ``outputs_node``), and
    extends ``_find_children`` to walk it via a new ``_find_inputs``
    classmethod, which mirrors the upstream ``_find_outputs`` implementation
    but reads ``process_node.inputs`` instead of ``process_node.outputs``.

    Notes
    -----
    A process/sub-process node whose type is not one of ``WorkChainNode``,
    ``CalcFunctionNode`` or ``CalcJobNode`` falls back to the upstream
    ``UnknownTypeTreeNode`` and will not get an "inputs" branch.
    """

    NODE_TYPE = {  # noqa: RUF012 - mirrors the upstream class attribute exactly
        orm.WorkChainNode: WorkChainProcessTreeNodeWithInputs,
        orm.CalcFunctionNode: CalcFunctionTreeNodeWithInputs,
        orm.CalcJobNode: CalcJobTreeNodeWithInputs,
    }

    @classmethod
    def _find_inputs(cls, root):
        """
        Generate all (including nested) input nodes of a process.

        A direct mirror of the upstream ``NodesTreeWidget._find_outputs``,
        substituting ``process_node.inputs`` for ``process_node.outputs``.

        Parameters
        ----------
        root : AiidaInputsTreeNode
            The "inputs" folder tree node being expanded.

        Yields
        ------
        ipytree.Node
            Either a nested :class:`AiidaInputsTreeNode` namespace folder, or
            a concrete tree node for an individual input AiiDA node.
        """
        process_node = orm.load_node(root.parent_pk)

        inputs = functools.reduce(
            lambda attr_dict, namespace: attr_dict[namespace],
            root.namespaces or [],
            process_node.inputs,
        )
        input_nodes = {key: inputs[key] for key in inputs}

        for key in sorted(
            input_nodes.keys(), key=lambda k: getattr(inputs[k], "pk", -1)
        ):
            node = input_nodes[key]
            if isinstance(node, common.AttributeDict):
                # For namespace tree nodes, attach a label and recurse.
                yield AiidaInputsTreeNode(
                    name=key,
                    parent_pk=root.parent_pk,
                    namespaces=(*root.namespaces, key),
                )
            else:
                if node.pk not in root.nodes_registry:
                    root.nodes_registry[node.pk] = cls._to_tree_node(
                        node, name=f"{key}<{node.pk}>"
                    )
                yield root.nodes_registry[node.pk]

    @classmethod
    def _find_children(cls, root):
        """
        Find all children of the provided tree node.

        Extends the upstream dispatcher with a branch for
        :class:`AiidaInputsTreeNode` roots (checked before the more general
        ``AiidaOutputsTreeNode``, since ``AiidaInputsTreeNode`` subclasses
        it), and yields ``root.inputs_node`` for process roots alongside the
        existing ``outputs_node``/called-process branches.

        Parameters
        ----------
        root : ipytree.Node
            The tree node being expanded.

        Yields
        ------
        ipytree.Node
            Child tree nodes.
        """
        if isinstance(root, AiidaProcessNodeTreeNode):
            # Only tree-node classes mixed in via ``_TreeNodeWithInputsMixin``
            # (i.e. everything reachable through our overridden ``NODE_TYPE``)
            # carry an ``inputs_node``; guard for the ``UnknownTypeTreeNode``
            # fallback, which does not.
            inputs_node = getattr(root, "inputs_node", None)
            if inputs_node is not None:
                yield inputs_node
            yield root.outputs_node
            yield from cls._find_called(root)
        elif isinstance(root, AiidaInputsTreeNode):
            yield from cls._find_inputs(root)
        elif isinstance(root, AiidaOutputsTreeNode):
            yield from cls._find_outputs(root)

    def _observe_tree_selected_nodes(self, change):
        """
        Handle a change in which tree nodes are selected.

        Overrides the upstream implementation to additionally pass through
        whether the selected node is an "inputs" folder, since
        :meth:`find_node` needs that to disambiguate it from an "outputs"
        folder of the same process (see :meth:`find_node`).

        Parameters
        ----------
        change : dict
            A traitlets change dictionary for the underlying ``ipytree.Tree``
            widget's ``selected_nodes`` trait.
        """
        for node in change["new"]:
            node_pk = (
                node.parent_pk
                if isinstance(node, AiidaOutputsTreeNode)
                else getattr(node, "pk", None)
            )
            self._build_tree(
                self.find_node(
                    node_pk,
                    getattr(node, "namespaces", None),
                    is_input=isinstance(node, AiidaInputsTreeNode),
                )
            )
        return self.set_trait(
            "selected_nodes",
            tuple(
                orm.load_node(pk=node.pk)
                for node in change["new"]
                if hasattr(node, "pk")
            ),
        )

    def find_node(self, pk, namespaces=None, is_input=False):
        """
        Find a node by its pk, namespaces, and inputs/outputs disambiguator.

        The upstream implementation identifies a folder node solely by
        ``(parent_pk, namespaces)``, which is not unique here: since
        :class:`AiidaInputsTreeNode` subclasses ``AiidaOutputsTreeNode``, the
        "inputs" and "outputs" folders of the same process (and of any shared
        nested namespace name) have an identical ``(parent_pk, namespaces)``
        key. Without this override, looking up either folder always resolves
        to whichever one ``_find_children`` yields first (the "inputs"
        folder), so clicking "outputs" would incorrectly expand "inputs".

        Parameters
        ----------
        pk : int
            Primary key of the node, or of its parent process if looking up
            an "inputs"/"outputs" folder.
        namespaces : tuple[str, ...], optional
            Namespace path, for a nested "inputs"/"outputs" folder lookup.
        is_input : bool
            Whether the folder being looked up is an "inputs" folder (as
            opposed to an "outputs" folder). Ignored for non-folder nodes.

        Returns
        -------
        ipytree.Node
            The matching tree node.

        Raises
        ------
        KeyError
            If no matching node is found.
        """
        for node in self._walk_tree(self._tree):
            if isinstance(node, AiidaOutputsTreeNode):
                if isinstance(node, AiidaInputsTreeNode) != is_input:
                    continue
                node_pk = node.parent_pk
            else:
                if is_input:
                    continue
                node_pk = getattr(node, "pk", None)
            if node_pk == pk and getattr(node, "namespaces", None) == namespaces:
                return node
        raise KeyError(pk)


class ProcessNodesTreeWidget(AiiDAlabProcessNodesTreeWidget):
    """
    Drop-in replacement for ``aiidalab_widgets_base.ProcessNodesTreeWidget``.

    Exposes the same ``value``/``selected_nodes`` traits as the upstream
    widget, but the underlying tree also shows an "inputs" branch (nodes
    linked via ``INPUT_CALC``/``INPUT_WORK`` links) alongside the existing
    "outputs" and "called" branches, for every process and sub-process in the
    tree.
    """

    def __init__(self, title="Process Tree", **kwargs):
        """
        Construct the widget.

        Parameters
        ----------
        title : str
            Passed straight through for compatibility with the upstream
            widget (consumed by ``ProcessFollowerWidget``).
        **kwargs
            Forwarded to :class:`ipywidgets.VBox`.
        """
        self.title = title
        self._tree = NodesTreeWidgetWithInputs()
        self._tree.observe(self._observe_tree_selected_nodes, ["selected_nodes"])
        ipw.VBox.__init__(self, children=[self._tree], **kwargs)
        self.update()
