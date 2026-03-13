#!/usr/bin/env python3
"""
generate_markmind.py

Generates an Obsidian MarkMind Rich format .md file from a JSON brainstorming outline.

Input (stdin): JSON with structure:
{
  "root": "🎯 Central Theme",
  "branches": [
    {
      "text": "🔴 Branch One",
      "color": "#ff6b6b",
      "children": [
        {
          "text": "⚙️ Sub A",
          "children": [
            { "text": "Detail 1" },
            { "text": "Detail 2" }
          ]
        }
      ]
    }
  ]
}

Output: .md file ready for Obsidian MarkMind plugin (Rich mode).

Usage:
  echo '{"root":"...","branches":[...]}' | python generate_markmind.py --output map.md
  python generate_markmind.py --output map.md --input outline.json
"""

import json
import sys
import argparse
import uuid
import math


# ── Layout Constants ──────────────────────────────────────────────

ROOT_X = 4120
ROOT_Y = 3700

# Horizontal offsets per level (from parent)
OFFSET_L2 = 280
OFFSET_L3 = 150
OFFSET_L4 = 140

# Vertical spacing between sibling nodes
V_SPACING = 33

# Gap between branch clusters
BRANCH_GAP = 12


def generate_id(prefix="node"):
    """Generate a short unique ID."""
    short = uuid.uuid4().hex[:12]
    return f"{prefix}-{short}"


def slugify(text, max_len=12):
    """Create a short slug from text for readable IDs."""
    clean = ""
    for ch in text.lower():
        if ch.isalnum():
            clean += ch
        elif ch == " " and clean and clean[-1] != "-":
            clean += "-"
    return clean.strip("-")[:max_len]


def count_leaves(branch):
    """Count the total number of leaf (terminal) nodes in a branch subtree."""
    children = branch.get("children", [])
    if not children:
        return 1
    return sum(count_leaves(c) for c in children)


def build_nodes(outline):
    """
    Convert the brainstorming outline into a flat list of MarkMind nodes
    with calculated coordinates.
    """
    nodes = []
    root_text = outline["root"]
    branches = outline.get("branches", [])

    # ── Root node ──
    root_id = generate_id("root")
    nodes.append({
        "id": root_id,
        "text": root_text,
        "isRoot": True,
        "main": True,
        "x": ROOT_X,
        "y": ROOT_Y,
        "isExpand": True,
        "layout": {"layoutName": "mindmap6", "direct": "mindmap"},
        "stroke": "",
        "style": {
            "color": "#ffffff",
            "background-color": "#ffffff",
            "border-color": "#ffffff",
            "text-align": "center"
        }
    })

    n_branches = len(branches)
    if n_branches == 0:
        return nodes

    # ── Split branches: right side (first half+extra), left side (second half) ──
    n_right = math.ceil(n_branches / 2)
    right_branches = branches[:n_right]
    left_branches = branches[n_right:]

    # ── Calculate total leaf count per side to center vertically ──
    def side_leaf_count(branch_list):
        total = 0
        for b in branch_list:
            total += count_leaves(b)
        # Add gaps between branches
        total_gaps = max(0, len(branch_list) - 1)
        return total, total_gaps

    def layout_side(branch_list, side, start_y_offset):
        """
        Layout all branches on one side.
        side: 'right' or 'left'
        start_y_offset: y offset from ROOT_Y for the first leaf of this side
        """
        sign = 1 if side == "right" else -1
        x_l2 = ROOT_X + sign * OFFSET_L2
        x_l3 = ROOT_X + sign * (OFFSET_L2 + OFFSET_L3)
        x_l4 = ROOT_X + sign * (OFFSET_L2 + OFFSET_L3 + OFFSET_L4)

        current_y = start_y_offset

        for branch in branch_list:
            color = branch.get("color", "#888888")
            branch_id = generate_id("br")
            branch_leaves = count_leaves(branch)

            # Branch L2 node y = center of its leaf span
            branch_y_start = current_y
            branch_y_end = current_y + (branch_leaves - 1) * V_SPACING
            branch_y = (branch_y_start + branch_y_end) / 2

            nodes.append({
                "id": branch_id,
                "text": branch["text"],
                "stroke": color,
                "style": {},
                "x": x_l2,
                "y": round(branch_y),
                "layout": None,
                "isExpand": True,
                "pid": root_id
            })

            children_l3 = branch.get("children", [])
            if not children_l3:
                current_y += V_SPACING + BRANCH_GAP
                continue

            # Layout L3 children
            l3_y_cursor = branch_y_start
            for child_l3 in children_l3:
                child_l3_id = generate_id("n3")
                child_l3_leaves = count_leaves(child_l3)

                l3_y_start = l3_y_cursor
                l3_y_end = l3_y_cursor + (child_l3_leaves - 1) * V_SPACING
                l3_y = (l3_y_start + l3_y_end) / 2

                nodes.append({
                    "id": child_l3_id,
                    "text": child_l3["text"],
                    "stroke": color,
                    "style": {},
                    "x": x_l3,
                    "y": round(l3_y),
                    "layout": None,
                    "isExpand": True,
                    "pid": branch_id
                })

                # Layout L4 children
                children_l4 = child_l3.get("children", [])
                l4_y_cursor = l3_y_start
                for child_l4 in children_l4:
                    child_l4_id = generate_id("n4")

                    nodes.append({
                        "id": child_l4_id,
                        "text": child_l4["text"],
                        "stroke": color,
                        "style": {},
                        "x": x_l4,
                        "y": round(l4_y_cursor),
                        "layout": None,
                        "isExpand": True,
                        "pid": child_l3_id
                    })
                    l4_y_cursor += V_SPACING

                # If no L4 children, the L3 node itself is a leaf
                if not children_l4:
                    l3_y_cursor += V_SPACING
                else:
                    l3_y_cursor = l4_y_cursor

            current_y = l3_y_cursor + BRANCH_GAP

    # ── Calculate vertical extents ──
    right_leaves, right_gaps = side_leaf_count(right_branches)
    left_leaves, left_gaps = side_leaf_count(left_branches)

    right_total_height = (right_leaves - 1) * V_SPACING + right_gaps * BRANCH_GAP
    left_total_height = (left_leaves - 1) * V_SPACING + left_gaps * BRANCH_GAP

    # Center both sides around ROOT_Y
    right_start_y = ROOT_Y - right_total_height / 2
    left_start_y = ROOT_Y - left_total_height / 2

    layout_side(right_branches, "right", right_start_y)
    layout_side(left_branches, "left", left_start_y)

    return nodes


def generate_free_nodes(count=8):
    """Generate empty free nodes as required by MarkMind Rich format."""
    free = []
    for _ in range(count):
        free.append([{
            "id": generate_id("fn"),
            "text": "freeNode",
            "main": False,
            "x": 0,
            "y": 0,
            "layout": {"layoutName": "mindmap2", "direct": "mindmap"},
            "isExpand": True,
            "stroke": "",
            "style": {}
        }])
    return free


def build_markmind_json(nodes):
    """Assemble the complete MarkMind Rich JSON structure."""
    free_nodes = generate_free_nodes(8)
    mind_data = [nodes] + free_nodes

    return {
        "theme": "",
        "mindData": mind_data,
        "induceData": [],
        "wireFrameData": [],
        "relateLinkData": [],
        "calloutData": [],
        "opt": {
            "background": "transparent",
            "fontFamily": "",
            "fontSize": 16
        },
        "scrollLeft": ROOT_X - 817,
        "scrollTop": ROOT_Y - 370,
        "transformOrigin": [ROOT_X + 133.5, ROOT_Y + 160]
    }


def wrap_markdown(json_str):
    """Wrap JSON in MarkMind Rich markdown format."""
    return f"""---

mindmap-plugin: rich

---

# Root
``` json
{json_str}
```
"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate Obsidian MarkMind Rich .md file from brainstorming outline"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output .md file path"
    )
    parser.add_argument(
        "--input", "-i",
        default=None,
        help="Input JSON file (default: stdin)"
    )
    args = parser.parse_args()

    # Read input
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            outline = json.load(f)
    else:
        outline = json.load(sys.stdin)

    # Validate
    if "root" not in outline:
        print("Error: JSON must have a 'root' key", file=sys.stderr)
        sys.exit(1)
    if "branches" not in outline:
        print("Error: JSON must have a 'branches' key", file=sys.stderr)
        sys.exit(1)

    # Build
    nodes = build_nodes(outline)
    markmind = build_markmind_json(nodes)
    json_str = json.dumps(markmind, ensure_ascii=False, separators=(",", ":"))

    # Write
    md_content = wrap_markdown(json_str)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Summary
    node_count = len(nodes)
    l2_count = sum(1 for n in nodes if n.get("pid") and not any(
        nn.get("pid") == n["id"] for nn in nodes
    ) == False and n.get("pid") == nodes[0]["id"])

    print(f"Generated: {args.output}", file=sys.stderr)
    print(f"Total nodes: {node_count}", file=sys.stderr)


if __name__ == "__main__":
    main()
