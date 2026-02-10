# -*- coding: utf-8 -*-
"""
ao_renamer_poc_UI.py

Renamer PoC - UI module (v0.1.0)
- PySide6
- Dockable via MayaQWidgetDockableMixin
- Collect inputs and call system.run_rename()
"""

from __future__ import annotations

from typing import Optional

import maya.cmds as cmds

from PySide6 import QtCore, QtWidgets

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# system import (same folder/module)
import ao_renamer_poc_system as renamer_system


# -----------------------------------------------------------------------------
# UI Constants
# -----------------------------------------------------------------------------

WINDOW_TITLE = "ao_renamer_poc"
WORKSPACE_CONTROL_NAME = "ao_renamer_pocWorkspaceControl"


# -----------------------------------------------------------------------------
# Main Window
# -----------------------------------------------------------------------------

class AoRenamerPocWindow(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    """
    Dockable Renamer UI
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(WINDOW_TITLE)
        self.setObjectName(WINDOW_TITLE)

        self.setMinimumWidth(360)

        self._build_ui()
        self._connect_signals()
        self._refresh_version_label()

    # -------------------------
    # UI construction
    # -------------------------

    def _build_ui(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Header
        header_row = QtWidgets.QHBoxLayout()
        header_row.setSpacing(8)

        self.title_label = QtWidgets.QLabel("Renamer PoC")
        font = self.title_label.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        self.title_label.setFont(font)

        self.version_label = QtWidgets.QLabel("v?.?.?")
        self.version_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        header_row.addWidget(self.title_label, 1)
        header_row.addWidget(self.version_label, 0)

        main_layout.addLayout(header_row)

        # Form area
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignLeft)
        form.setFormAlignment(QtCore.Qt.AlignTop)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(6)

        self.prefix_le = QtWidgets.QLineEdit()
        self.prefix_le.setPlaceholderText("例: GEO / CTRL (自動で大文字化)")

        self.base_le = QtWidgets.QLineEdit()
        self.base_le.setPlaceholderText("例: head / spine / arm")

        self.suffix_le = QtWidgets.QLineEdit()
        self.suffix_le.setPlaceholderText("例: grp / jnt (自動で小文字化)")

        self.start_index_sb = QtWidgets.QSpinBox()
        self.start_index_sb.setRange(1, 999999)
        self.start_index_sb.setValue(1)

        self.padding_sb = QtWidgets.QSpinBox()
        self.padding_sb.setRange(1, 6)
        self.padding_sb.setValue(2)

        form.addRow("Prefix", self.prefix_le)
        form.addRow("BaseName", self.base_le)
        form.addRow("Suffix", self.suffix_le)
        form.addRow("Start Index", self.start_index_sb)
        form.addRow("Padding", self.padding_sb)

        main_layout.addLayout(form)

        # Buttons
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(8)

        self.preview_btn = QtWidgets.QPushButton("Preview")
        self.rename_btn = QtWidgets.QPushButton("Rename")
        self.rename_btn.setDefault(True)

        btn_row.addWidget(self.preview_btn, 1)
        btn_row.addWidget(self.rename_btn, 1)

        main_layout.addLayout(btn_row)

        # Result / log
        self.log_te = QtWidgets.QPlainTextEdit()
        self.log_te.setReadOnly(True)
        self.log_te.setMinimumHeight(140)
        self.log_te.setPlaceholderText("ここに結果が表示されます。")

        main_layout.addWidget(self.log_te, 1)

        # Footer small note
        self.note_label = QtWidgets.QLabel("対象: 選択中の transform のみ / 重複は連番で回避")
        self.note_label.setStyleSheet("color: rgba(255,255,255,160);")
        main_layout.addWidget(self.note_label)

    def _connect_signals(self) -> None:
        self.preview_btn.clicked.connect(self.on_preview)
        self.rename_btn.clicked.connect(self.on_rename)

    def _refresh_version_label(self) -> None:
        try:
            self.version_label.setText(f"v{renamer_system.__version__}")
        except Exception:
            self.version_label.setText("v?.?.?")

    # -------------------------
    # Helpers
    # -------------------------

    def _collect_inputs(self) -> renamer_system.RenameInput:
        return renamer_system.RenameInput(
            prefix=self.prefix_le.text(),
            base_name=self.base_le.text(),
            suffix=self.suffix_le.text(),
            start_index=int(self.start_index_sb.value()),
            padding=int(self.padding_sb.value()),
        )

    def _log(self, text: str, clear: bool = False) -> None:
        if clear:
            self.log_te.setPlainText(text)
        else:
            current = self.log_te.toPlainText().rstrip()
            if current:
                self.log_te.setPlainText(current + "\n" + text)
            else:
                self.log_te.setPlainText(text)

        # scroll to end
        cursor = self.log_te.textCursor()
        cursor.movePosition(cursor.End)
        self.log_te.setTextCursor(cursor)

    def _warn_dialog(self, title: str, message: str) -> None:
        QtWidgets.QMessageBox.warning(self, title, message)

    # -------------------------
    # Slots
    # -------------------------

    def on_preview(self) -> None:
        """
        Preview planned new names.
        """
        try:
            inp = self._collect_inputs()
            selected = cmds.ls(selection=True) or []
            if not selected:
                self._warn_dialog("No Selection", "何も選択されていません。")
                return

            # system preview
            pairs = renamer_system.preview_names(inp)
            if not pairs:
                self._log("Preview: 対象 transform がありません。", clear=True)
                return

            lines = ["=== Preview ==="]
            for node, new_name in pairs:
                lines.append(f"{node}  ->  {new_name}")

            self._log("\n".join(lines), clear=True)

        except Exception as e:
            self._log(f"[Preview Failed] {e}", clear=False)

    def on_rename(self) -> None:
        """
        Execute rename via system.run_rename()
        """
        try:
            inp = self._collect_inputs()
            selected = cmds.ls(selection=True) or []
            if not selected:
                self._warn_dialog("No Selection", "何も選択されていません。")
                return

            summary = renamer_system.run_rename(inp)

            lines = []
            lines.append("=== Rename Result ===")
            lines.append(f"version: v{renamer_system.__version__}")
            lines.append(f"selected: {summary.total_selected} / targets(transform): {summary.total_targets}")
            lines.append(f"renamed: {summary.renamed}  skipped: {summary.skipped}  failed: {summary.failed}")
            lines.append("")

            for r in summary.results:
                if r.status == "renamed":
                    lines.append(f"[OK] {r.old_name} -> {r.new_name} ({r.message})")
                elif r.status == "skipped":
                    lines.append(f"[SKIP] {r.old_name} ({r.message})")
                else:
                    lines.append(f"[FAIL] {r.old_name} ({r.message})")

            self._log("\n".join(lines), clear=True)

        except Exception as e:
            self._log(f"[Rename Failed] {e}", clear=False)


# -----------------------------------------------------------------------------
# Show / Dock helpers
# -----------------------------------------------------------------------------

def _delete_workspace_control(name: str) -> None:
    """
    If workspaceControl exists, delete it to avoid duplicated docking.
    """
    if cmds.workspaceControl(name, exists=True):
        try:
            cmds.deleteUI(name)
        except Exception:
            pass


def show(dockable: bool = True) -> AoRenamerPocWindow:
    """
    Entry point to show window.
    dockable=True -> dockable workspaceControl
    """
    _delete_workspace_control(WORKSPACE_CONTROL_NAME)

    win = AoRenamerPocWindow()
    win.show(dockable=dockable, floating=True, area="right")
    return win


# -----------------------------------------------------------------------------
# Manual test (Script Editor)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    show(dockable=True)
