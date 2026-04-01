// Team Spawn Gate - UserPromptSubmit hook (advisory, not blocking)
// Detects team-worthy requests and suggests the matching team preset.
// Toggle: set "teamSpawnGate" to false in ~/.claude/acp-config.json to disable

const fs = require("fs");
const path = require("path");

const homeDir = process.env.HOME || process.env.USERPROFILE;
const acpConfigPath = path.join(homeDir, ".claude", "acp-config.json");

let enabled = true;
try {
  const config = JSON.parse(fs.readFileSync(acpConfigPath, "utf8"));
  if (config.teamSpawnGate === false) enabled = false;
} catch {
  // No config = enabled by default
}

if (!enabled) process.exit(0);

// Require agent teams feature flag -- no point suggesting teams if disabled
if (!process.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS) process.exit(0);

// --- Preset detection rules ---
// Each preset has:
//   phrases: high-confidence multi-word patterns (any match = suggest)
//   keywords + minWords: lower-confidence single words that need complexity confirmation
//   scopeBoost: words that lower the minWords threshold by 5

const PRESETS = [
  {
    name: "review",
    command: "/agent-teams:team-spawn review",
    shortCommand: "/senior-review:code-review",
    desc: "Multi-dimensional code review (security + architecture + performance)",
    phrases: [
      "code review", "full review", "comprehensive review",
      "review the code", "review this code", "review my code",
      "multi-dimensional review", "architecture review",
      "revisiona il codice", "revisione completa"
    ],
    keywords: ["review", "audit", "revisiona", "revisione"],
    minWords: 15,
    scopeBoost: ["comprehensive", "full", "thorough", "deep", "completa", "completo"]
  },
  {
    name: "security",
    command: "/agent-teams:team-spawn security",
    desc: "Security audit with OWASP, platform, and distributed flow analysis",
    phrases: [
      "security audit", "security scan", "vulnerability scan",
      "owasp audit", "pentest", "penetration test",
      "audit di sicurezza", "analisi sicurezza"
    ],
    keywords: ["security", "vulnerability", "owasp", "sicurezza"],
    minWords: 8,
    scopeBoost: ["comprehensive", "full", "complete", "completa"]
  },
  {
    name: "debug",
    command: "/agent-teams:team-debug",
    desc: "Competing hypotheses debugging with parallel investigation",
    phrases: [
      "competing hypotheses", "multiple causes", "parallel debug",
      "root cause analysis", "can't figure out why",
      "investigate with hypotheses", "debug in parallel",
      "ipotesi concorrenti", "cause multiple"
    ],
    keywords: ["debug", "investigate", "trace"],
    minWords: 25,
    scopeBoost: ["hypotheses", "causes", "parallel", "competing", "ipotesi"]
  },
  {
    name: "feature",
    command: "/agent-teams:team-feature",
    desc: "Parallel feature development with file ownership boundaries",
    phrases: [
      "build a feature", "implement the feature", "develop a feature",
      "parallel development", "parallel implementation",
      "sviluppa in parallelo", "implementa in parallelo"
    ],
    keywords: ["build", "implement", "create", "develop", "costruisci", "implementa"],
    minWords: 30,
    scopeBoost: ["parallel", "multiple files", "across", "end to end", "from scratch",
                  "da zero", "completo", "parallelo"]
  },
  {
    name: "fullstack",
    command: "/agent-teams:team-spawn fullstack",
    desc: "Full-stack development with frontend, backend, and test agents",
    phrases: [
      "full stack", "fullstack", "frontend and backend",
      "backend and frontend", "end to end feature",
      "full-stack", "frontend e backend"
    ],
    keywords: [],
    minWords: 10,
    scopeBoost: []
  },
  {
    name: "deep-search",
    command: "/agent-teams:team-research",
    desc: "Deep multi-source research with parallel investigators",
    phrases: [
      "deep research", "thorough research", "comprehensive research",
      "systematic investigation", "deep dive research",
      "ricerca approfondita", "ricerca sistematica"
    ],
    keywords: ["research", "investigate", "ricerca"],
    minWords: 20,
    scopeBoost: ["deep", "thorough", "comprehensive", "systematic", "approfondita"]
  },
  {
    name: "research",
    command: "/agent-teams:team-spawn research",
    desc: "Parallel codebase, web, and documentation research",
    phrases: [
      "research this topic", "find out how", "research across",
      "parallel research"
    ],
    keywords: [],
    minWords: 25,
    scopeBoost: ["parallel", "multiple sources", "codebase and web"]
  },
  {
    name: "migration",
    command: "/agent-teams:team-spawn migration",
    desc: "Large-scale migration or refactor with coordination",
    phrases: [
      "migrate from", "migration from", "port from", "upgrade from",
      "large refactor", "codebase migration", "large-scale refactor",
      "migra da", "migrazione da"
    ],
    keywords: ["migrate", "migration", "migra", "migrazione"],
    minWords: 12,
    scopeBoost: ["entire", "all", "codebase", "large", "complete", "tutto", "intero"]
  },
  {
    name: "docs",
    command: "/agent-teams:team-spawn docs",
    desc: "Parallel documentation generation with exploration + writing + review",
    phrases: [
      "document the codebase", "map the codebase", "generate documentation",
      "write documentation for", "comprehensive docs",
      "documenta il codice", "mappa il codebase"
    ],
    keywords: ["document", "documentation", "documenta", "documentazione"],
    minWords: 15,
    scopeBoost: ["entire", "full", "comprehensive", "codebase", "project", "completa"]
  },
  {
    name: "app-analysis",
    command: "/agent-teams:team-spawn app-analysis",
    desc: "Competitive app analysis with UX audit + research + design extraction",
    phrases: [
      "analyze the app", "competitor app", "competitive analysis",
      "reverse engineer the ui", "app audit", "ux audit",
      "analizza l'app", "analisi competitiva"
    ],
    keywords: [],
    minWords: 10,
    scopeBoost: ["competitor", "competitive", "reverse engineer"]
  },
  {
    name: "tauri",
    command: "/agent-teams:team-spawn tauri",
    desc: "Tauri desktop/mobile development with Rust + frontend + platform agents",
    phrases: [
      "tauri app", "tauri desktop", "tauri mobile",
      "build with tauri", "create a tauri", "develop a tauri"
    ],
    keywords: ["tauri"],
    minWords: 15,
    scopeBoost: ["from scratch", "full", "desktop", "mobile", "da zero"]
  },
  {
    name: "ui-studio",
    command: "/agent-teams:team-design",
    desc: "Parallel UI design and build pipeline (design + layout + UX + polish)",
    phrases: [
      "ui from scratch", "design from scratch", "redesign the ui",
      "build the ui", "design system from scratch", "new design system",
      "ui da zero", "redesign completo", "ridisegna la ui"
    ],
    keywords: ["redesign", "ridisegna"],
    minWords: 15,
    scopeBoost: ["from scratch", "complete", "entire", "da zero", "completo"]
  }
];

function countWords(text) {
  return text.split(/\s+/).filter(Boolean).length;
}

function matchPreset(prompt) {
  const lower = prompt.toLowerCase();
  const words = countWords(prompt);

  // Tier 1: phrase matching (high confidence)
  for (const preset of PRESETS) {
    for (const phrase of preset.phrases) {
      if (lower.includes(phrase)) {
        return preset;
      }
    }
  }

  // Tier 2: keyword + complexity matching
  for (const preset of PRESETS) {
    if (!preset.keywords.length) continue;

    const hasKeyword = preset.keywords.some(kw => {
      const re = new RegExp("\\b" + kw + "\\b", "i");
      return re.test(lower);
    });

    if (!hasKeyword) continue;

    // Apply scope boost: each matching scope word reduces minWords by 5
    let effectiveMin = preset.minWords;
    if (preset.scopeBoost) {
      const boostCount = preset.scopeBoost.filter(sw => lower.includes(sw)).length;
      effectiveMin = Math.max(5, effectiveMin - boostCount * 5);
    }

    if (words >= effectiveMin) {
      return preset;
    }
  }

  return null;
}

// --- Main ---

let input = "";
const stdinTimeout = setTimeout(() => process.exit(0), 3000);
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { input += chunk; });
process.stdin.on("end", () => {
  clearTimeout(stdinTimeout);
  try {
    const event = JSON.parse(input);
    const prompt = (event.prompt || "").trim();

    // Bypass: empty, slash commands, hash prefix, asterisk prefix
    if (!prompt || prompt.startsWith("/") || prompt.startsWith("#") || prompt.startsWith("*")) {
      process.exit(0);
    }

    // Bypass: single-word prompts
    if (!prompt.includes(" ")) process.exit(0);

    // Bypass: explicit --no-team flag
    if (prompt.includes("--no-team")) process.exit(0);

    // Bypass: questions (ends with ?)
    if (prompt.trimEnd().endsWith("?")) process.exit(0);

    const matched = matchPreset(prompt);
    if (!matched) process.exit(0);

    const context = [
      `<IMPORTANT>`,
      `[Team Spawn Gate] This prompt matches the "${matched.name}" team preset.`,
      ``,
      `The user's request appears complex enough to benefit from a multi-agent team.`,
      `Suggested command: ${matched.command}`,
      `What it does: ${matched.desc}`,
      ``,
      `You should:`,
      `1. Inform the user that their request could benefit from a team of parallel agents`,
      `2. Briefly explain what the "${matched.name}" team preset does`,
      `3. Ask if they want to proceed with the team, or handle it as a single-agent task`,
      `4. If they agree, invoke the team-spawn command: ${matched.command}`,
      ``,
      `If the user has already explicitly requested a specific approach, follow their instruction.`,
      `The user can add --no-team to any prompt to suppress this suggestion.`,
      `</IMPORTANT>`
    ].join("\n");

    const output = {
      hookSpecificOutput: {
        hookEventName: "UserPromptSubmit",
        additionalContext: context
      }
    };

    process.stdout.write(JSON.stringify(output));
  } catch {
    process.exit(0);
  }
});
