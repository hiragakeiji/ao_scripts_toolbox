# -*- coding: utf-8 -*-
"""
ao Locator Follow Rig Tool (single file)

Select 2 objects in order:
  Selection1 -> Selection2

Creates:
  locator + group
  group snapped to Selection2
  (optional) freeze group
  constraints with keepOffset ON:
    Selection1 -> group
    locator    -> Selection2

Maya 2025 / PySide6
"""

import maya.cmds as cmds

from PySide6 import QtCore, QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


# ------------------------------------------------------------
# Core logic (single-file, no split)
# ------------------------------------------------------------
def _get_transform(node):
    """Return transform even if a shape is selected."""
    if not node or not cmds.objExists(node):
        return node
    if cmds.nodeType(node) == "transform":
        return node
    parent = cmds.listRelatives(node, parent=True, fullPath=True) or []
    return parent[0] if parent else node


def _build_follow_rig(sel1, sel2, do_freeze=True):
    """
    sel1 -> group (parentConstraint, keepOffset ON)
    locator -> sel2 (parentConstraint, keepOffset ON)
    """
    sel1 = _get_transform(sel1)
    sel2 = _get_transform(sel2)

    cmds.undoInfo(openChunk=True)
    try:
        # Create locator (unique)
        locator = cmds.spaceLocator(name="ao_follow_loc#")[0]

        # Group locator (unique)
        grp = cmds.group(locator, name="ao_follow_grp#")

        # Snap group to Selection2 by world matrix
        m = cmds.xform(sel2, q=True, ws=True, m=True)
        cmds.xform(grp, ws=True, m=m)

        # Optional freeze (group)
        if do_freeze:
            cmds.makeIdentity(grp, apply=True, t=True, r=True, s=True, n=False)

        # Constraints (ALL keepOffset ON)
        cmds.parentConstraint(sel1, grp, mo=True)
        cmds.parentConstraint(locator, sel2, mo=True)

        # Select locator for convenience
        cmds.select(locator, r=True)

        print(f"[ao] Done: locator={locator}, group={grp}, freeze={do_freeze}")
        return locator, grp

    except Exception as e:
        cmds.warning(f"[ao] Failed: {e}")
        return None, None

    finally:
        cmds.undoInfo(closeChunk=True)


# ------------------------------------------------------------
# UI (single-file)
# ------------------------------------------------------------
_WINDOW_INSTANCE = None


class AoLocatorFollowRigTool(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    WINDOW_TITLE = "ao Locator Follow Rig Tool"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setObjectName("aoLocatorFollowRigTool_UI")
        self.setMinimumWidth(420)

        self._build_ui()
        self._connect()

    def _build_ui(self):
        self.setMinimumWidth(200)

        title = QtWidgets.QLabel(self.WINDOW_TITLE)
        title.setAlignment(QtCore.Qt.AlignCenter)
        f = title.font()
        f.setPointSize(max(10, f.pointSize() + 2))
        title.setFont(f)

        self.btn_apply = QtWidgets.QPushButton("apply")
        self.btn_apply.setMinimumHeight(44)

        # checkbox row
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        self.lbl_freeze = QtWidgets.QLabel("ロケーターのフリーズ")
        self.chk_freeze = QtWidgets.QCheckBox()
        self.chk_freeze.setChecked(True)

        row.addWidget(self.lbl_freeze)
        row.addStretch(1)
        row.addWidget(self.chk_freeze)
    
        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(18, 16, 18, 16)
        main.setSpacing(12)
        main.addWidget(title)
        main.addSpacing(6)
        main.addWidget(self.btn_apply)
        main.addLayout(row)


    def _connect(self):
        self.btn_apply.clicked.connect(self.on_apply)

    def on_apply(self):
        sel = cmds.ls(sl=True, long=True) or []
        if len(sel) != 2:
            cmds.warning("2つ選択してください（Selection1 → Selection2）")
            return

        do_freeze = self.chk_freeze.isChecked()
        _build_follow_rig(sel[0], sel[1], do_freeze=do_freeze)


def show():
    """Show UI (dockable, starts floating)."""
    global _WINDOW_INSTANCE

    # Dock名（Qt objectName + "WorkspaceControl" で Maya が作る）
    dock_name = "aoLocatorFollowRigTool_UIWorkspaceControl"

    # 既存の WorkspaceControl を削除（★これが重要）
    if cmds.workspaceControl(dock_name, q=True, exists=True):
        cmds.deleteUI(dock_name)

    # 既存ウィンドウ削除
    try:
        if _WINDOW_INSTANCE is not None:
            _WINDOW_INSTANCE.close()
            _WINDOW_INSTANCE.deleteLater()
    except Exception:
        pass

    _WINDOW_INSTANCE = AoLocatorFollowRigTool()

    # floating first (dockable available)
    _WINDOW_INSTANCE.show(dockable=True, floating=True)

    return _WINDOW_INSTANCE

# Run
show()
