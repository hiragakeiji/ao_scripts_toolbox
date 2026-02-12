# -*- coding: utf-8 -*-
"""
ao_LocatorFollowRigTool_UI.py

Maya 2025 / PySide6
Dockable UI (floating first)

"""

import maya.cmds as cmds

from PySide6 import QtCore, QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import ao_LocatorFollowRigTool_system as system


_WINDOW_INSTANCE = None


class AoLocatorFollowRigTool(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    WINDOW_TITLE = "ao Locator Follow Rig Tool"
    OBJECT_NAME = "aoLocatorFollowRigTool_UI" 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setObjectName(self.OBJECT_NAME)
        self.setMinimumWidth(200)

        self._build_ui()
        self._connect()

    def _build_ui(self):
        title = QtWidgets.QLabel(self.WINDOW_TITLE)
        title.setAlignment(QtCore.Qt.AlignCenter)
        f = title.font()
        f.setPointSize(max(10, f.pointSize() + 2))
        title.setFont(f)

        self.btn_apply = QtWidgets.QPushButton("apply")
        self.btn_apply.setMinimumHeight(44)

        self.lbl_freeze = QtWidgets.QLabel("ロケーターのフリーズ")
        self.chk_freeze = QtWidgets.QCheckBox()
        self.chk_freeze.setChecked(True)  # default ON

        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
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
        do_freeze = self.chk_freeze.isChecked()
        system.build_follow_rig(do_freeze=do_freeze)


def _delete_existing_workspace_control():
    """
    既存の WorkspaceControl が残っていると
    '...WorkspaceControl が固有ではありません' が出るので先に消す。
    """
    dock_name = AoLocatorFollowRigTool.OBJECT_NAME + "WorkspaceControl"
    if cmds.workspaceControl(dock_name, q=True, exists=True):
        cmds.deleteUI(dock_name)


def run():
    """Entry point for shelf button."""
    global _WINDOW_INSTANCE

    _delete_existing_workspace_control()

    try:
        if _WINDOW_INSTANCE is not None:
            _WINDOW_INSTANCE.close()
            _WINDOW_INSTANCE.deleteLater()
    except Exception:
        pass

    _WINDOW_INSTANCE = AoLocatorFollowRigTool()
    _WINDOW_INSTANCE.show(dockable=True, floating=True)
    return _WINDOW_INSTANCE
