# -*- coding: utf-8 -*-
"""
ao_LocatorFollowRigTool_download.py  (Drag & Drop installer)

Policy:
- scripts:  Documents/maya/scripts  ONLY (avoid duplicates)
- icons:    keep version+locale candidates for safety
- shelf:    add/replace button on shelf "tool"
"""

import os
import shutil

import maya.cmds as cmds
import maya.mel as mel


TOOL_SHELF_NAME = "tool"
MODULE_UI = "ao_LocatorFollowRigTool_UI"
ICON_FILE = "ao_LocatorFollowRigTool_icon.png"

BTN_LABEL = "ao Locator Follow Rig Tool"      # ← シェルフ上の「名前」
BTN_ANNOTATION = "ao Locator Follow Rig Tool" # ← ツールヒント
BTN_OVERLAY = ""                              # ← アイコン上のラベルは空

FILES_TO_COPY = [
    "ao_LocatorFollowRigTool_UI.py",
    "ao_LocatorFollowRigTool_system.py",
]


def _this_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


def _ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _copy_file(src, dst_dir):
    _ensure_dir(dst_dir)
    dst = os.path.join(dst_dir, os.path.basename(src))
    shutil.copy2(src, dst)
    return dst


def _get_user_maya_root():
    # e.g. C:/Users/<you>/Documents/maya/
    return cmds.internalVar(userAppDir=True).replace("\\", "/").rstrip("/")


def _get_maya_version():
    return str(cmds.about(version=True))


# ----------------------------
# IMPORTANT: scripts is ONLY one place
# Documents/maya/scripts
# ----------------------------
def _scripts_target_single():
    root = _get_user_maya_root()
    return f"{root}/scripts"


def _icons_candidates():
    # アイコンは Maya の読み込み順が環境差あるので安全に2箇所へ
    root = _get_user_maya_root()
    ver = _get_maya_version()
    return [
        f"{root}/{ver}/prefs/icons",
        f"{root}/{ver}/ja_JP/prefs/icons",
    ]


def _ensure_shelf_exists(shelf_name):
    shelf_top = mel.eval("$tmp = $gShelfTopLevel")
    if cmds.shelfLayout(shelf_name, q=True, exists=True):
        return
    cmds.shelfLayout(shelf_name, parent=shelf_top)


def _remove_existing_buttons(shelf_name):
    """同じツール（annotation一致）のボタンを削除して増殖を防ぐ"""
    if not cmds.shelfLayout(shelf_name, q=True, exists=True):
        return

    children = cmds.shelfLayout(shelf_name, q=True, ca=True) or []
    for c in children:
        if cmds.objectTypeUI(c) != "shelfButton":
            continue
        try:
            ann = cmds.shelfButton(c, q=True, annotation=True) or ""
            # annotation が一致するものを置換対象にする
            if ann == BTN_ANNOTATION:
                cmds.deleteUI(c)
        except Exception:
            pass


def _add_shelf_button(shelf_name, icon_name):
    _ensure_shelf_exists(shelf_name)
    _remove_existing_buttons(shelf_name)

    cmd = f"import {MODULE_UI} as m\nm.run()"

    cmds.shelfButton(
        parent=shelf_name,
        label=BTN_LABEL,             # ← ★名前（空にならない）
        annotation=BTN_ANNOTATION,   # ← ツールヒント
        image=icon_name,
        imageOverlayLabel=BTN_OVERLAY,  # ← ★アイコン上のラベルは空
        command=cmd,
        sourceType="python",
    )


def install():
    src_dir = _this_dir()

    # --- copy scripts (ONLY Documents/maya/scripts)
    scripts_dst = _scripts_target_single()
    copied_scripts = []

    for fname in FILES_TO_COPY:
        src = os.path.join(src_dir, fname)
        if not os.path.isfile(src):
            cmds.warning(f"[ao] missing file: {src}")
            continue
        try:
            copied_scripts.append(_copy_file(src, scripts_dst))
        except Exception as e:
            cmds.warning(f"[ao] copy failed: {scripts_dst} ({e})")

    # --- copy icon
    icon_src = os.path.join(src_dir, ICON_FILE)
    copied_icons = []
    if os.path.isfile(icon_src):
        for dst_dir in _icons_candidates():
            try:
                copied_icons.append(_copy_file(icon_src, dst_dir))
            except Exception as e:
                cmds.warning(f"[ao] icon copy failed: {dst_dir} ({e})")
    else:
        cmds.warning(f"[ao] missing icon: {icon_src}")

    # --- add shelf button
    try:
        _add_shelf_button(TOOL_SHELF_NAME, ICON_FILE)
    except Exception as e:
        cmds.warning(f"[ao] shelf button failed: {e}")

    # --- feedback
    print("[ao_LocatorFollowRigTool] Installed!")
    if copied_scripts:
        print(" - scripts copied:")
        for p in copied_scripts:
            print("   ", p)
    if copied_icons:
        print(" - icons copied:")
        for p in copied_icons:
            print("   ", p)
    print(f" - shelf: {TOOL_SHELF_NAME}")
    print(f" - command: import {MODULE_UI} as m; m.run()")


def onMayaDroppedPythonFile(*args, **kwargs):
    install()
