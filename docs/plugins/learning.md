# Learning Plugin

> Generate mind maps in Obsidian MarkMind Rich format from any content -- books, articles, topics, notes, or conversations.

## Skills

### `markmind-mapper`

Generate mind maps in Obsidian MarkMind Rich JSON format. Output is a `.md` file ready to drop into an Obsidian vault with the MarkMind plugin.

| | |
|---|---|
| **Invoke** | Skill reference or `/build-mindmap` |
| **Use for** | Mind maps, concept maps, visual summaries, brainstorming, content extraction |

**Workflow:**
1. **Brainstorm** -- identify central theme, extract 5-7 main branches (L2), sub-concepts (L3), leaf details (L4)
2. **Generate** -- pipe JSON outline to `generate_markmind.py` script with emoji and color assignments
3. **Output** -- ready-to-use `.md` file for Obsidian MarkMind plugin

**Includes:**
- `references/markmind-rich-spec.md` -- MarkMind Rich format specification
- `scripts/generate_markmind.py` -- JSON-to-MarkMind generator script

---

## Commands

### `/build-mindmap`

Generate a MarkMind mind map from any topic, text, or file.

```
/build-mindmap Python asyncio patterns
/build-mindmap "text to map"
/build-mindmap path/to/file.md
```

**Output:** `.md` file ready for Obsidian MarkMind plugin.
