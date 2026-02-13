# -*- coding: utf-8 -*-
"""
ao_LocatorFollowRigTool_UI.py  (cmds UI version)

Maya 2024 and earlier compatible (no PySide6 required)

Shelf command:
    import ao_LocatorFollowRigTool_UI as m
    m.run()
"""

import maya.cmds as cmds
import ao_LocatorFollowRigTool_system as system

WIN_NAME = "aoLocatorFollowRigTool_win"
WIN_TITLE = "ao Locator Follow Rig Tool"

# control names
CHK_FREEZE = "chkFreeze"
BTN_APPLY  = "aoLocatorFollowRigTool_btnApply"


def _close_existing():
    if cmds.window(WIN_NAME, exists=True):
        cmds.deleteUI(WIN_NAME)


def _on_apply(*args):
    do_freeze = cmds.checkBox(CHK_FREEZE, q=True, v=True)
    system.build_follow_rig(do_freeze=do_freeze)


def run():
    """Entry point"""
    _close_existing()

    # window
    cmds.window(WIN_NAME, title=WIN_TITLE, sizeable=True, widthHeight=(300, 160))

    # --- layout
    # 画像みたいにシンプルに：タイトル / apply / フリーズチェック
    cmds.columnLayout(adj=True, rowSpacing=6, columnAlign="center")

    cmds.text(label=WIN_TITLE, align="center")
    cmds.separator(style="none", height=6)

    cmds.button(
        BTN_APPLY,
        label="apply",
        height=34,
        command=_on_apply
    )

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAlign=(1, "left"), columnAttach=[(1, "both", 0), (2, "right", 0)])
    cmds.text(label="ロケーターのフリーズ")
    cmds.checkBox(CHK_FREEZE, v=True)  # default ON
    cmds.setParent("..")  # rowLayout end

    cmds.separator(style="none", height=3)

    cmds.showWindow(WIN_NAME)
    return WIN_NAME
