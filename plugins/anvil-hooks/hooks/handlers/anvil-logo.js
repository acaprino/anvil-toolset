// Anvil ASCII Logo - SessionStart hook
// Prints the Anvil banner when Claude Code or Gemini CLI starts

const logo = `
\x1b[38;2;139;110;72m        ___
       / _ \\
      | |_) |
       \\___/\x1b[0m
\x1b[38;2;108;130;145m    \u2554\u2550\u2550\u2550\u2567\u2550\u2550\u2550\u2557
    \u2551       \u2551
    \u2560\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2563
    \u2551       \u2551
    \u255a\u2550\u2550\u2564\u2550\u2564\u2550\u2550\u255d
   \u2550\u2550\u2550\u2550\u2567\u2550\u2567\u2550\u2550\u2550\u2550\x1b[0m

\x1b[38;2;180;190;200m   \u2554\u2550\u2557 \u2566\u2557\u2566 \u2566  \u2566 \u2566 \u2566
   \u2560\u2550\u2563 \u2551\u2551\u2551 \u255a\u2557\u2554\u255d \u2551 \u2551
   \u2569 \u2569 \u255d\u255a\u255d  \u255a\u255d  \u2569 \u2569\u2550\u255d\x1b[0m
\x1b[2m   AI Code Session Launcher\x1b[0m
`;

console.log(logo);
