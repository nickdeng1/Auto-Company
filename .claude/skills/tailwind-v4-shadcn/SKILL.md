---
name: tailwind-v4-shadcn
description: |
  Production-tested setup for Tailwind CSS v4 with shadcn/ui, Vite, and React.

  Use when: initializing React projects with Tailwind v4, setting up shadcn/ui,
  implementing dark mode, debugging CSS variable issues, fixing theme switching,
  migrating from Tailwind v3, or encountering color/theming problems.

  Covers: @theme inline pattern, CSS variable architecture, dark mode with
  ThemeProvider, component composition, vite.config setup, common v4 gotchas,
  and production-tested patterns.

  Keywords: Tailwind v4, shadcn/ui, @tailwindcss/vite, @theme inline, dark mode,
  CSS variables, hsl() wrapper, components.json, React theming, theme switching,
  colors not working, variables broken, theme not applying, @plugin directive,
  typography plugin, forms plugin, prose class, @tailwindcss/typography,
  @tailwindcss/forms
license: MIT
---

# Tailwind v4 + shadcn/ui Production Stack

**Production-tested**: WordPress Auditor (https://wordpress-auditor.webfonts.workers.dev)
**Last Updated**: 2025-12-04
**Status**: Production Ready ✅

## Table of Contents
1. [Before You Start](#-before-you-start-read-this)
2. [Quick Start](#quick-start-5-minutes---follow-this-exact-order)
3. [Four-Step Architecture](#the-four-step-architecture-critical)
4. [Dark Mode Setup](#dark-mode-setup)
5. [Critical Rules](#critical-rules-must-follow)
6. [Semantic Color Tokens](#semantic-color-tokens)
7. [Common Issues & Fixes](#common-issues--quick-fixes)
8. [File Templates](#file-templates)
9. [Setup Checklist](#complete-setup-checklist)
10. [Advanced Topics](#advanced-topics)
11. [Dependencies](#dependencies)
12. [Tailwind v4 Plugins](#tailwind-v4-plugins)
13. [Reference Documentation](#reference-documentation)
14. [When to Load References](#when-to-load-references)

---

## ⚠️ BEFORE YOU START (READ THIS!)

**CRITICAL FOR AI AGENTS**: If you're Claude Code helping a user set up Tailwind v4:

1. **Explicitly state you're using this skill** at the start of the conversation
2. **Reference patterns from the skill** rather than general knowledge
3. **Prevent known issues** listed in `reference/common-gotchas.md`
4. **Don't guess** - if unsure, check the skill documentation

**USER ACTION REQUIRED**: Tell Claude to check this skill first!

Say: **"I'm setting up Tailwind v4 + shadcn/ui - check the tailwind-v4-shadcn skill first"**

### Why This Matters (Real-World Results)

**Without skill activation:**
- ❌ Setup time: ~5 minutes
- ❌ Errors encountered: 2-3 (tw-animate-css, duplicate @layer base)
- ❌ Manual fixes needed: 2+ commits
- ❌ Token usage: ~65k
- ❌ User confidence: Required debugging

**With skill activation:**
- ✅ Setup time: ~1 minute
- ✅ Errors encountered: 0
- ✅ Manual fixes needed: 0
- ✅ Token usage: ~20k (70% reduction)
- ✅ User confidence: Instant success

### Known Issues This Skill Prevents

1. **tw-animate-css import error** (deprecated in v4)
2. **Duplicate @layer base blocks** (shadcn init adds its own)
3. **Wrong template selection** (vanilla TS vs React)
4. **Missing post-init cleanup** (incompatible CSS rules)
5. **Wrong plugin syntax** (using @import or require() instead of @plugin directive)

All of these are handled automatically when the skill is active.

---

## Quick Start (5 Minutes - Follow This Exact Order)

### 1. Install Dependencies

```bash
bun add tailwindcss @tailwindcss/vite
# or: npm install tailwindcss @tailwindcss/vite

bun add -d @types/node

# Note: Using pnpm for shadcn init due to known Bun compatibility issues
# (bunx has "Script not found" and postinstall/msw problems)
pnpm dlx shadcn@latest init
```

### 2. Configure Vite

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

### 3. Update components.json

```json
{
  "tailwind": {
    "config": "",              // ← CRITICAL: Empty for v4
    "css": "src/index.css",
    "cssVariables": true
  }
}
```

### 4. Delete tailwind.config.ts

```bash
rm tailwind.config.ts  # v4 doesn't use this file
```

---

