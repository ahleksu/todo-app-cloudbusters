---
name: "pdf-user-guide-generator"
displayName: "PDF User Guide Generator"
description: "Generates PDF user guides for frontend applications by exploring the codebase, launching the app locally, and screenshotting every page and interactive state using Playwright."
keywords: ["pdf", "user-guide", "screenshot", "playwright", "documentation"]
author: "Alex"
---

# PDF User Guide Generator

## Overview

This power automates the creation of comprehensive PDF user guides for frontend applications. It explores your codebase to discover all routes and interactive elements, launches the app locally, uses Playwright to screenshot every page and interactive state (modals, tabs, drawers, dropdowns), and compiles everything into a structured PDF document.

The final deliverable is always a PDF file — never HTML or Markdown. The PDF includes a cover page, table of contents, and one section per route with embedded screenshots and step-by-step usage instructions inferred from the UI and source code.

## Available Steering Files

- **workflow** — Complete step-by-step execution workflow for generating the PDF user guide

## Onboarding

### Prerequisites

- Node.js 16+ installed
- Python 3.8+ installed (for PDF generation with fpdf2)
- A frontend application with a dev server (supports Nuxt, Next.js, React, Vue, Svelte, etc.)
- Playwright MCP server configured in Kiro

### Playwright MCP Setup

This power requires the Playwright MCP server. If not already configured, add it to your MCP settings:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-playwright"]
    }
  }
}
```

### Python Dependencies

The PDF generation step requires `fpdf2`. It will be installed automatically during execution:

```bash
pip install fpdf2
```

## Rules (Follow Strictly)

1. **The final output must be a PDF file.** Never produce HTML or Markdown as the deliverable.
2. **Always use absolute file paths** when referencing screenshots. Never use relative paths.
3. **Visit every route in the app.** Do not stop at the homepage.
4. **Capture interactive states** (modals, tabs, drawers, dropdowns) — not just static pages.
5. **Confirm the PDF file exists and is non-empty** before finishing.

## Workflow Steps

### Step 1: Discover All Routes

Scan the codebase before opening a browser. Check:

- Router config files (react-router, vue-router, next.js pages/app dir, svelte-kit, nuxt)
- Any `<Link>`, `<NavLink>`, `<a href>`, `router.push`, `navigate()` usages
- Sidebar/nav components

Build a complete route list and note interactive elements per route (modals, tabs, drawers, accordions, forms).

**Framework-specific locations:**
| Framework | Route Source |
|-----------|-------------|
| Nuxt 3 | `pages/` directory structure |
| Next.js | `pages/` or `app/` directory |
| React Router | Router config, `<Route>` components |
| Vue Router | `router/index.ts` or `router.js` |
| SvelteKit | `src/routes/` directory |

### Step 2: Install Dependencies and Start the App

1. Run `npm install` in the frontend directory
2. Install Playwright: `npm install -D playwright && npx playwright install chromium`
3. Start the dev server: `npm run dev &`
4. Poll `http://localhost:<port>` until the server responds (up to 30s)
5. Check `vite.config`, `next.config`, or `package.json` for the port; default to 3000

### Step 3: Screenshot Every Page and State

Use the Playwright MCP to control a real Chromium browser. For each route:

1. Navigate and wait for `networkidle` or `domcontentloaded` + a short delay
2. Take a full-page screenshot saved to `./user-guide-assets/screenshots/` with a descriptive deterministic filename (e.g., `page-dashboard.png` — no timestamps or random strings)
3. Trigger each interactive element and save an additional screenshot with a descriptive suffix (e.g., `page-dashboard-modal-add-user.png`)
4. Log every screenshot's absolute path

**Filename conventions:**
- Page screenshots: `page-{route-name}.png`
- Interactive states: `page-{route-name}-{element-type}-{element-name}.png`
- Examples: `page-login.png`, `page-todos-modal-create-todo.png`, `page-todos-dropdown-filter.png`

### Step 4: Build a Screenshot Manifest

Before generating the PDF, verify every file exists and compile an absolute-path manifest:

```json
[
  {
    "route": "/",
    "label": "Home",
    "screenshots": ["/abs/path/page-home.png"]
  },
  {
    "route": "/login",
    "label": "Login",
    "screenshots": ["/abs/path/page-login.png"]
  }
]
```

### Step 5: Generate the PDF

Install `fpdf2` and write a Python script to build the PDF.

**Do NOT use** weasyprint, pdfkit, or any HTML-to-PDF tool.

The script must:
1. Load screenshots from the manifest using **absolute paths**
2. Call `os.path.exists()` on each image before embedding (print a warning and skip if missing — do not crash)
3. Structure the PDF as:
   - **Cover page**: App name, "User Guide", generation date
   - **Table of contents**: With page numbers
   - **One section per route**: Heading, screenshots with captions, numbered step-by-step usage guide inferred from the UI and source code

Save to `./user-guide.pdf` and print its absolute path. If the file is missing or 0 bytes after running, debug and retry.

### Step 6: Verify Before Finishing

Confirm:
- Every discovered route has at least one screenshot
- Every interactive state has a screenshot
- `./user-guide.pdf` exists and is non-empty
- PDF sections contain embedded screenshots (not broken placeholders)

Report the absolute path to `user-guide.pdf` and list all pages documented.

## Troubleshooting

### Playwright MCP Not Responding

**Problem:** Browser doesn't launch or tools timeout
**Solution:**
1. Verify Playwright is installed: `npx playwright install chromium`
2. Check MCP server is configured correctly
3. Restart Kiro and try again

### Dev Server Won't Start

**Problem:** `npm run dev` fails or port is occupied
**Solution:**
1. Check for port conflicts: `lsof -i :3000`
2. Kill existing processes: `kill $(lsof -t -i:3000)`
3. Verify `package.json` has a `dev` script
4. Check for missing dependencies: `npm install`

### Screenshots Are Blank or Incomplete

**Problem:** Pages not fully rendered in screenshots
**Solution:**
1. Increase wait time after navigation (add 2-3 second delay)
2. Use `networkidle` wait condition
3. Check if the app requires authentication — log in first
4. Verify the route exists and renders content

### PDF Generation Fails

**Problem:** Python script errors or empty PDF
**Solution:**
1. Verify `fpdf2` is installed: `pip install fpdf2`
2. Check all image paths in manifest exist
3. Ensure images are valid PNG files
4. Check Python version (3.8+ required)

### Missing Routes

**Problem:** Not all pages are captured
**Solution:**
1. Check for dynamic routes (e.g., `/todos/:id`)
2. Look for auth-protected routes — ensure login is performed first
3. Check for conditional rendering based on state
4. Review navigation components for hidden links

## Best Practices

- Always scan the codebase for routes BEFORE launching the browser
- Use deterministic filenames (no timestamps or UUIDs) for reproducibility
- Capture both the default state and all interactive states of each page
- Verify screenshots exist before attempting PDF generation
- Use absolute paths throughout to avoid path resolution issues
- If the app requires authentication, perform login before capturing protected routes
- Add short delays after triggering interactive elements to allow animations to complete

## Configuration

**No additional configuration required** beyond having the Playwright MCP server installed in Kiro.

The power uses:
- **Playwright MCP** — For browser automation and screenshots
- **fpdf2** (Python) — For PDF generation
- **Project's dev server** — Launched automatically during execution

---

**MCP Server:** playwright
**PDF Engine:** fpdf2 (Python)
