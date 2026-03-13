---
name: markmind-mapper
description: "Generate mind maps in Obsidian MarkMind Rich format from any content (books, articles, topics, notes, conversations). Use this skill whenever the user asks to create a mind map, mappa mentale, mappa concettuale, concept map, or visual summary for Obsidian. Also trigger when the user says 'markmind', 'mindmap', 'mind map', 'mappa', or asks to visualize/map/schematize any content. The skill handles brainstorming, content extraction, hierarchy design, and outputs a .md file ready to paste into an Obsidian vault with the MarkMind plugin."
---

# MarkMind Mapper

Generate mind maps in Obsidian MarkMind Rich JSON format. The output is a `.md` file the user can drop directly into their Obsidian vault and open with the MarkMind plugin.

## Workflow

### Phase 1: Brainstorming (internal, not shown to user)

Before generating any JSON, analyze the input content and produce an internal outline:

1. **Identify the central theme** in 2-4 words
2. **Extract 5-7 main branches** (L2). Each branch is a core concept, not a chapter title. Think: "What are the 5-7 ideas that, together, reconstruct the whole?"
3. **For each branch, extract 2-4 sub-concepts** (L3). Each is a keyword or micro-phrase (2-4 words max)
4. **For each sub-concept, extract 1-3 leaf details** (L4). Single keyword or keyword pair
5. **Assign emoji** to every L2 and L3 node using the semantic code below
6. **Assign colors** to each L2 branch from the palette

Do NOT skip this phase. The quality of the map depends entirely on the brainstorming outline.

### Phase 2: Generation

Run the Python script `scripts/generate_markmind.py` passing the brainstorming outline as a JSON structure. The script handles coordinate calculation, node assembly, and file output.

### Phase 3: Delivery

Present the generated `.md` file to the user. Mention it's ready to drop into Obsidian.

## Content Principles

Follow the E-Myth model: **complete coverage, balanced branches, equal weight across all L2 rami**. No Pareto filtering. The goal is a comprehensive visual reference, not a highlight reel.

- Every node = **keyword or micro-phrase**, never a full sentence
- Prefer nouns and action verbs; strip articles and prepositions
- Causal/sequential relations: use `→` in node text
- Opposites/tensions: use `≠` or `↔` or `⚡`
- Never use the em dash character

### Emoji Semantic Code

| Function                     | Emoji |
| ---------------------------- | ----- |
| Central concept / nucleus    | 🎯    |
| Definition / "what is it"    | 📌    |
| Process / sequence           | ⚙️    |
| Risk / warning               | ⚠️    |
| Advantage / strength         | ✅    |
| Disadvantage / limit         | ❌    |
| Concrete example             | 💡    |
| Cross-branch link            | 🔗    |
| Open question / explore      | ❓    |
| Numeric data / metric        | 📊    |
| Person / role                | 👤    |
| Time / phase                 | ⏳    |

Add domain-specific emoji where useful (🧠 psychology, 💻 tech, 💰 finance, 📖 book, etc.). Emoji always goes **before** the keyword.

### Color Palette (L2 branches)

| Branch # | Hex       | Name       |
| -------- | --------- | ---------- |
| 1        | #ff6b6b   | Coral      |
| 2        | #4ecdc4   | Teal       |
| 3        | #95e77e   | Lime       |
| 4        | #a8e6cf   | Mint       |
| 5        | #ffd3b6   | Peach      |
| 6        | #d4a5f5   | Lavender   |
| 7        | #f7dc6f   | Yellow     |
| 8        | #85c1e9   | Sky        |

All descendants inherit the stroke color of their L2 ancestor.

## How to Use the Script

Read `references/markmind-rich-spec.md` for the full JSON schema if needed.

The script accepts a JSON outline on stdin and writes the `.md` file:

```bash
cat <<'EOF' | python scripts/generate_markmind.py --output /path/to/output.md --title "Map Title"
{
  "root": "🎯 Central Theme",
  "branches": [
    {
      "text": "🔴 Branch One",
      "color": "#ff6b6b",
      "children": [
        {
          "text": "⚙️ Sub-concept A",
          "children": [
            { "text": "Detail 1" },
            { "text": "Detail 2" }
          ]
        },
        {
          "text": "📌 Sub-concept B",
          "children": []
        }
      ]
    }
  ]
}
EOF
```

The script automatically:
- Generates unique node IDs
- Splits branches left/right of root
- Calculates x/y coordinates with proper spacing
- Creates 8 empty free nodes
- Wraps everything in valid MarkMind Rich format

## Checklist Before Delivery

- All `pid` references point to existing `id` values
- Root has `isRoot: true`, `main: true`, layout object
- No `pid` on root node
- Each L2 branch has a unique stroke color
- All descendants inherit their L2 ancestor's stroke
- Coordinates don't overlap (V_SPACING respected)
- JSON is valid (no trailing commas, balanced brackets)
- 8 empty free nodes present
- Emoji on all L2 and L3 nodes
- Max 4 levels of depth
