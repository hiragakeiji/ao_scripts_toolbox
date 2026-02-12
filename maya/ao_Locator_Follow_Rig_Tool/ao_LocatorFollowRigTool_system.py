# -*- coding: utf-8 -*-
"""
ao_LocatorFollowRigTool_system.py

Core system:
- Select 2 objects in order: Selection1 -> Selection2
- Create locator + group
- Snap group to Selection2
- Optional freeze (toggle from UI)
- ParentConstraints (ALL keepOffset ON)
    Selection1 -> group
    locator    -> Selection2
"""

import maya.cmds as cmds


def _get_transform(node: str) -> str:
    """Return transform even if a shape is selected."""
    if not node or not cmds.objExists(node):
        return node

    if cmds.nodeType(node) == "transform":
        return node

    parent = cmds.listRelatives(node, parent=True, fullPath=True) or []
    return parent[0] if parent else node


def build_follow_rig(do_freeze: bool = True):
    """
    Execute rig build from current selection.
    Returns (locator, group) or (None, None) on failure.
    """
    sel = cmds.ls(sl=True, long=True) or []
    if len(sel) != 2:
        cmds.warning("[ao] 2つ選択してください（Selection1 → Selection2）")
        return None, None

    sel1 = _get_transform(sel[0])
    sel2 = _get_transform(sel[1])

    cmds.undoInfo(openChunk=True)
    try:
        # unique names
        locator = cmds.spaceLocator(name="ao_follow_loc#")[0]
        grp = cmds.group(locator, name="ao_follow_grp#")

        # snap group to Selection2 (world matrix)
        m = cmds.xform(sel2, q=True, ws=True, m=True)
        cmds.xform(grp, ws=True, m=m)

        # optional freeze
        if do_freeze:
            cmds.makeIdentity(grp, apply=True, t=True, r=True, s=True, n=False)

        # constraints (ALL keepOffset ON)
        cmds.parentConstraint(sel1, grp, mo=True)
        cmds.parentConstraint(locator, sel2, mo=True)

        # select locator for convenience
        cmds.select(locator, r=True)

        print(f"[ao] Done: locator={locator}, group={grp}, freeze={do_freeze}")
        return locator, grp

    except Exception as e:
        cmds.warning(f"[ao] Failed: {e}")
        return None, None

    finally:
        cmds.undoInfo(closeChunk=True)
