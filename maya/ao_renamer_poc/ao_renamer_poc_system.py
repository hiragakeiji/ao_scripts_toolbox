# -*- coding: utf-8 -*-
"""
ao_renamer_poc_system.py

Renamer PoC - system module (v0.1.0)
- Selection-based rename (transform only)
- Name rule: [prefix]_[baseName]_[suffix]_[index]
- Collision avoidance: increment index until unique
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import maya.cmds as cmds


__version__ = "0.1.2"


# ----------------------------
# Data structures
# ----------------------------

@dataclass
class RenameInput:
    prefix: str = ""
    base_name: str = ""
    suffix: str = ""
    start_index: int = 1
    padding: int = 2  # 2 -> 01, 02


@dataclass
class RenameItemResult:
    node: str
    old_name: str
    new_name: Optional[str]
    status: str  # "renamed" / "skipped" / "failed"
    message: str = ""


@dataclass
class RenameSummary:
    inputs: RenameInput
    total_selected: int
    total_targets: int
    renamed: int
    skipped: int
    failed: int
    results: List[RenameItemResult]


# ----------------------------
# Public API
# ----------------------------

def run_rename(rename_input: RenameInput) -> RenameSummary:
    """
    Main entry point.
    - Collect selection (transform only)
    - Build names
    - Avoid collisions
    - Execute rename
    """
    selected = _get_selection(long_name=True)
    targets = _filter_transforms(selected)

    results: List[RenameItemResult] = []
    index = max(1, int(rename_input.start_index))

    for node in targets:
        old = node

        try:
            # Validate node exists
            if not cmds.objExists(node):
                results.append(RenameItemResult(
                    node=node, old_name=old, new_name=None,
                    status="failed", message="Node does not exist."
                ))
                continue

            # Create unique new name
            new_name, used_index = _build_unique_name(
                rename_input=rename_input,
                start_index=index
            )

            # If we cannot create a name (shouldn't happen), skip
            if not new_name:
                results.append(RenameItemResult(
                    node=node, old_name=old, new_name=None,
                    status="skipped", message="New name is empty."
                ))
                continue

            # Perform rename (keep hierarchy path stable)
            renamed_node = cmds.rename(node, new_name)

            results.append(RenameItemResult(
                node=renamed_node, old_name=old, new_name=new_name,
                status="renamed", message=f"Used index: {used_index}"
            ))

            # Next node should start from used_index + 1
            index = used_index + 1

        except Exception as e:
            results.append(RenameItemResult(
                node=node, old_name=old, new_name=None,
                status="failed", message=str(e)
            ))
            # Even if failed, we still increment to avoid repeating same index forever
            index += 1

    summary = _summarize(rename_input, selected, targets, results)
    return summary


def preview_names(rename_input: RenameInput) -> List[Tuple[str, str]]:
    """
    Preview rename results without executing rename.
    Returns list of (node, preview_new_name).
    - This preview uses collision avoidance against current scene names.
    - It does not account for renames changing later collisions in sequence perfectly,
      but it's good enough for UI preview in v0.1.0.
    """
    selected = _get_selection(long_name=True)
    targets = _filter_transforms(selected)

    previews: List[Tuple[str, str]] = []
    index = max(1, int(rename_input.start_index))

    for _ in targets:
        new_name, used_index = _build_unique_name(rename_input, index)
        previews.append(("", new_name))
        index = used_index + 1

    # Attach node names after (keep simple)
    return [(targets[i], previews[i][1]) for i in range(len(targets))]


# ----------------------------
# Core helpers
# ----------------------------

def _get_selection(long_name: bool = True) -> List[str]:
    """
    Get current selection. Return [] if nothing.
    long_name=True returns full DAG path (safer when duplicates exist).
    """
    sel = cmds.ls(selection=True, long=long_name) or []
    return sel


def _filter_transforms(nodes: List[str]) -> List[str]:
    """
    Keep only transform nodes.
    - If a shape is selected, convert to its parent transform.
    - Remove duplicates while preserving order.
    """
    seen = set()
    out: List[str] = []

    for n in nodes:
        if not cmds.objExists(n):
            continue

        node_type = cmds.nodeType(n)
        if node_type == "transform":
            t = n
        else:
            # If it's a shape, try to get its parent transform
            parents = cmds.listRelatives(n, parent=True, fullPath=True) or []
            t = parents[0] if parents else None

        if not t or not cmds.objExists(t):
            continue

        if cmds.nodeType(t) != "transform":
            continue

        if t not in seen:
            seen.add(t)
            out.append(t)

    return out


def _sanitize_token(s: str) -> str:
    """
    Sanitize for Maya node name tokens.
    v0.1.0: minimal sanitization:
      - strip spaces
      - replace spaces with underscore
      - remove leading/trailing underscores
    (You can expand later: illegal chars, unicode handling, etc.)
    """
    if s is None:
        return ""
    s = str(s).strip()
    s = s.replace(" ", "_")
    s = s.strip("_")
    return s


def _format_prefix(prefix: str) -> str:
    p = _sanitize_token(prefix)
    return p.upper() if p else ""


def _format_suffix(suffix: str) -> str:
    s = _sanitize_token(suffix)
    return s.lower() if s else ""


def _format_base(base_name: str) -> str:
    return _sanitize_token(base_name)


def _compose_name(prefix: str, base_name: str, suffix: str, index: int, padding: int) -> str:
    """
    Compose name tokens with "_" auto insertion.
    Empty tokens are ignored.
    """
    tokens = []

    p = _format_prefix(prefix)
    b = _format_base(base_name)
    s = _format_suffix(suffix)

    if p:
        tokens.append(p)
    if b:
        tokens.append(b)
    if s:
        tokens.append(s)

    # Index token is always appended (renamer spec)
    idx_token = str(int(index)).zfill(max(1, int(padding)))
    tokens.append(idx_token)

    return "_".join(tokens)


def _short_name_exists(name: str) -> bool:
    """
    Maya name collisions are effectively on short name level in many operations.
    We'll check both exact and wildcard matches to be safe.

    - cmds.objExists("name") checks existence of that name (short or long)
    - But long path could exist even if short name is ambiguous.
    So we also check cmds.ls(name) length.
    """
    if not name:
        return False
    if cmds.objExists(name):
        return True
    matches = cmds.ls(name) or []
    return len(matches) > 0


def _build_unique_name(rename_input: RenameInput, start_index: int) -> Tuple[str, int]:
    """
    Generate a unique name by incrementing index until unused.
    Returns (unique_name, used_index).
    """
    idx = max(1, int(start_index))
    padding = max(1, int(rename_input.padding))

    # In v0.1.0, we treat uniqueness by short-name existence check.
    # For DAG, Maya can allow same short name in different groups,
    # but rename often becomes ambiguous and is risky.
    # So we enforce scene-unique short name.
    while True:
        candidate = _compose_name(
            prefix=rename_input.prefix,
            base_name=rename_input.base_name,
            suffix=rename_input.suffix,
            index=idx,
            padding=padding,
        )

        if not _short_name_exists(candidate):
            return candidate, idx

        idx += 1

        # Safety break (avoid infinite loop)
        if idx > 999999:
            raise RuntimeError("Could not find unique name (index overflow).")


def _summarize(rename_input: RenameInput, selected: List[str], targets: List[str], results: List[RenameItemResult]) -> RenameSummary:
    renamed = sum(1 for r in results if r.status == "renamed")
    skipped = sum(1 for r in results if r.status == "skipped")
    failed = sum(1 for r in results if r.status == "failed")

    return RenameSummary(
        inputs=rename_input,
        total_selected=len(selected),
        total_targets=len(targets),
        renamed=renamed,
        skipped=skipped,
        failed=failed,
        results=results,
    )


# ----------------------------
# Debug / Manual test (optional)
# ----------------------------

def _debug_print_summary(summary: RenameSummary) -> None:
    """
    Helper for debugging in Script Editor.
    """
    print("=== ao_renamer_poc summary ===")
    print(f"version: {__version__}")
    print(f"selected: {summary.total_selected}, targets(transform): {summary.total_targets}")
    print(f"renamed: {summary.renamed}, skipped: {summary.skipped}, failed: {summary.failed}")
    for r in summary.results:
        print(f"[{r.status}] {r.old_name} -> {r.new_name} | {r.message}")
