
import py_trees

from src.recovery.nodes import (
    CheckStopped,
    CheckDiagnostic,
    CheckInterlocks,
    WaitForAcknowledgement,
    AcknowledgeFault,
    CheckFaultResolved,
    ClearFault,
    WaitForRestartApproval,
    AuthorizeAndRestart,
)


def create_recovery_tree(context):
    root = py_trees.composites.Sequence(
        name="FactoryGuard Recovery Sequence",
        memory=False,
    )

    root.add_children([
        CheckStopped(context),
        CheckDiagnostic(context),
        CheckInterlocks(context),
        WaitForAcknowledgement(context),
        AcknowledgeFault(context),
        CheckFaultResolved(context),
        ClearFault(context),
        WaitForRestartApproval(context),
        AuthorizeAndRestart(context),
    ])

    tree = py_trees.trees.BehaviourTree(root)
    tree.setup(timeout=5.0)

    return tree
