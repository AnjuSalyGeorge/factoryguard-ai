
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
    """
    Create the FactoryGuard AI recovery behaviour tree.

    The recovery sequence preserves deterministic
    safety checks and explicit operator approval.

    Streamlit executes dashboard code in a separate
    script thread.

    py_trees.common.Duration.INFINITE allows tree
    setup without registering a Python signal handler,
    making initialization compatible with Streamlit.

    Note:
        This removes the setup timeout only.
        It does not disable machine safety checks,
        operator acknowledgment, or restart approval.
    """

    # --------------------------------------------------
    # 1. Create Recovery Sequence
    # --------------------------------------------------

    root = py_trees.composites.Sequence(
        name="FactoryGuard Recovery Sequence",
        memory=False,
    )

    # --------------------------------------------------
    # 2. Add Recovery Safety Nodes
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 3. Create Behaviour Tree
    # --------------------------------------------------

    tree = py_trees.trees.BehaviourTree(root)

    # --------------------------------------------------
    # 4. Initialize Without Signal Registration
    # --------------------------------------------------

    # The installed py_trees implementation skips
    # signal handling when timeout is INFINITE.
    #
    # This is necessary because Streamlit executes
    # application code outside the main Python thread.

    tree.setup(
        timeout=py_trees.common.Duration.INFINITE
    )

    # --------------------------------------------------
    # 5. Return Initialized Recovery Tree
    # --------------------------------------------------

    return tree
