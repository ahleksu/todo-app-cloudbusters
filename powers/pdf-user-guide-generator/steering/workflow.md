# PDF User Guide Generation — Detailed Execution Workflow

This steering file provides the complete step-by-step execution instructions for generating a PDF user guide. Follow these steps in order.

---

## Pre-Flight Checks

Before starting, verify:
1. The frontend project directory exists and has a `package.json`
2. The Playwright MCP server is available (test with a simple browser launch)
3. Python 3.8+ is available on the system

---

## Step 1: Discover All Routes

### 1.1 Identify the Framework

Read `package.json` to determine the frontend framework:
- **Nuxt 3**: Look for `nuxt` in dependencies → routes in `pages/` directory
- **Next.js**: Look for `next` → routes in `pages/` or `app/` directory
- **React (CRA/Vite)**: Look for `react-router-dom` → routes in router config
- **Vue**: Look for `vue-router` → routes in `router/index.ts`
- **SvelteKit**: Look for `@sveltejs/kit` → routes in `src/routes/`

### 1.2 Scan Route Sources

**For Nuxt 3 (pages directory convention):**
```
pages/
├── index.vue        → /
├── login.vue        → /login
├── register.vue     → /register
├── dashboard.vue    → /dashboard
└── todos/
    ├── index.vue    → /todos
    └── [id].vue     → /todos/:id
```

**For React Router:**
- Search for `<Route path=`, `createBrowserRouter`, route config arrays
- Check `App.tsx`, `routes.tsx`, or similar files

**For Vue Router:**
- Read `src/router/index.ts` or `src/router/index.js`
- Extract all `path` values from route definitions

### 1.3 Scan for Interactive Elements

For each route's component file, search for:
- **Modals**: `v-if`, `v-show`, `isOpen`, `showModal`, `dialog`, `Modal` components
- **Tabs**: `tab`, `TabPanel`, `activeTab`, tab-related state
- **Drawers**: `drawer`, `sidebar`, `isDrawerOpen`, slide-over components
- **Dropdowns**: `dropdown`, `select`, `menu`, `Popover`, `Listbox`
- **Accordions**: `accordion`, `collapse`, `expandable`
- **Forms**: `<form>`, `@submit`, `onSubmit`, form validation states
- **Tooltips**: `tooltip`, `title` attributes on interactive elements

### 1.4 Build Route Manifest

Create a structured list:
```
Route: /
  Label: Home
  Interactive elements: none

Route: /login
  Label: Login
  Interactive elements: form (login form), validation states

Route: /todos
  Label: Todos List
  Interactive elements: modal (create todo), dropdown (filter), dropdown (sort)

Route: /todos/:id
  Label: Todo Detail
  Interactive elements: modal (edit), modal (delete confirm)
```

---

## Step 2: Install Dependencies and Start the App

### 2.1 Install Frontend Dependencies

```bash
cd {frontend-directory}
npm install
```

### 2.2 Install Playwright

```bash
npm install -D playwright
npx playwright install chromium
```

### 2.3 Install PDF Dependencies

```bash
pip install fpdf2
```

### 2.4 Determine the Port

Check in this order:
1. `vite.config.ts` or `vite.config.js` → look for `server.port`
2. `next.config.js` → look for port configuration
3. `nuxt.config.ts` → look for `devServer.port`
4. `package.json` → look for port in `dev` script
5. Default: 3000

### 2.5 Start the Dev Server

```bash
npm run dev &
```

### 2.6 Poll Until Ready

Poll `http://localhost:{port}` every 2 seconds for up to 30 seconds:
```bash
for i in $(seq 1 15); do
  if curl -s http://localhost:{port} > /dev/null 2>&1; then
    echo "Server is ready"
    break
  fi
  sleep 2
done
```

---

## Step 3: Screenshot Every Page and State

### 3.1 Create Screenshots Directory

```bash
mkdir -p ./user-guide-assets/screenshots
```

### 3.2 Screenshot Workflow Per Route

For each route in the manifest:

1. **Navigate** to the route using Playwright MCP `browser_navigate`
2. **Wait** for page to be fully loaded (use `browser_wait_for_load_state` with networkidle, or add a 2-second delay)
3. **Take full-page screenshot** using `browser_screenshot`
   - Save to: `./user-guide-assets/screenshots/page-{route-name}.png`
   - Use absolute path for the save location
4. **For each interactive element:**
   - Trigger the element (click button, open modal, switch tab, etc.) using `browser_click`
   - Wait for animation/transition (1-2 second delay)
   - Take screenshot: `./user-guide-assets/screenshots/page-{route-name}-{element-type}-{element-name}.png`
   - Close/reset the element if needed before moving to next

### 3.3 Filename Convention

Use descriptive, deterministic filenames:
- `page-home.png` — Homepage default state
- `page-login.png` — Login page
- `page-login-form-validation-error.png` — Login with validation errors
- `page-todos.png` — Todos list default state
- `page-todos-modal-create-todo.png` — Create todo modal open
- `page-todos-dropdown-filter-status.png` — Status filter dropdown open
- `page-todos-modal-delete-confirm.png` — Delete confirmation dialog

**Rules:**
- No timestamps
- No random strings or UUIDs
- All lowercase with hyphens
- Descriptive and deterministic

### 3.4 Handle Authentication

If the app has protected routes:
1. First navigate to the login/register page
2. Fill in credentials and submit
3. Wait for redirect/auth cookie to be set
4. Then proceed to capture protected routes

### 3.5 Log All Screenshots

After each screenshot, log its absolute path:
```
Screenshot saved: /absolute/path/to/user-guide-assets/screenshots/page-home.png
Screenshot saved: /absolute/path/to/user-guide-assets/screenshots/page-login.png
...
```

---

## Step 4: Build Screenshot Manifest

### 4.1 Verify All Files Exist

For each expected screenshot, verify the file exists on disk using `os.path.exists()` or `ls`.

### 4.2 Compile Manifest

Create a JSON manifest with absolute paths:

```json
[
  {
    "route": "/",
    "label": "Home",
    "screenshots": [
      "/absolute/path/user-guide-assets/screenshots/page-home.png"
    ]
  },
  {
    "route": "/login",
    "label": "Login",
    "screenshots": [
      "/absolute/path/user-guide-assets/screenshots/page-login.png",
      "/absolute/path/user-guide-assets/screenshots/page-login-form-validation-error.png"
    ]
  },
  {
    "route": "/todos",
    "label": "Todos",
    "screenshots": [
      "/absolute/path/user-guide-assets/screenshots/page-todos.png",
      "/absolute/path/user-guide-assets/screenshots/page-todos-modal-create-todo.png",
      "/absolute/path/user-guide-assets/screenshots/page-todos-dropdown-filter.png"
    ]
  }
]
```

### 4.3 Validate Completeness

Check:
- Every route has at least one screenshot
- Every noted interactive element has a corresponding screenshot
- All file paths resolve to existing, non-empty files

---

## Step 5: Generate the PDF

### 5.1 Write the Python Script

Create a Python script (`generate_pdf.py`) that:

```python
import json
import os
from datetime import datetime
from fpdf import FPDF

# Load manifest
with open('manifest.json', 'r') as f:
    manifest = json.load(f)

# Create PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# --- Cover Page ---
pdf.add_page()
pdf.set_font('Helvetica', 'B', 36)
pdf.cell(0, 60, '', ln=True)  # spacing
pdf.cell(0, 20, '{App Name}', ln=True, align='C')
pdf.set_font('Helvetica', '', 24)
pdf.cell(0, 15, 'User Guide', ln=True, align='C')
pdf.set_font('Helvetica', '', 14)
pdf.cell(0, 15, f'Generated: {datetime.now().strftime("%Y-%m-%d")}', ln=True, align='C')

# --- Table of Contents ---
pdf.add_page()
pdf.set_font('Helvetica', 'B', 20)
pdf.cell(0, 15, 'Table of Contents', ln=True)
pdf.set_font('Helvetica', '', 12)
# (Add TOC entries with page numbers after building all sections)

# --- Sections per Route ---
for entry in manifest:
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, f'{entry["label"]} ({entry["route"]})', ln=True)
    pdf.ln(5)

    for screenshot_path in entry['screenshots']:
        if os.path.exists(screenshot_path):
            # Add screenshot
            pdf.image(screenshot_path, x=10, w=190)
            pdf.ln(5)
            # Add caption
            filename = os.path.basename(screenshot_path)
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 8, f'Figure: {filename}', ln=True, align='C')
            pdf.ln(3)
        else:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 8, f'[WARNING: Screenshot missing: {screenshot_path}]', ln=True)
            print(f'WARNING: Screenshot missing: {screenshot_path}')

    # Add usage guide
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'How to Use This Page', ln=True)
    pdf.set_font('Helvetica', '', 11)
    # (Infer steps from UI elements and source code)

# Save PDF
output_path = os.path.join(os.getcwd(), 'user-guide.pdf')
pdf.output(output_path)
print(f'PDF generated: {output_path}')

# Verify
if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
    print(f'SUCCESS: PDF is {os.path.getsize(output_path)} bytes')
else:
    print('ERROR: PDF is missing or empty!')
    exit(1)
```

### 5.2 Run the Script

```bash
python generate_pdf.py
```

### 5.3 Handle Failures

If the PDF is missing or 0 bytes:
1. Check Python error output
2. Verify image paths in manifest
3. Ensure fpdf2 is installed correctly
4. Debug and retry

---

## Step 6: Final Verification

### 6.1 Checklist

- [ ] Every discovered route has at least one screenshot
- [ ] Every interactive state (modal, tab, drawer, dropdown) has a screenshot
- [ ] `./user-guide.pdf` exists
- [ ] `./user-guide.pdf` is non-empty (> 0 bytes)
- [ ] PDF contains embedded screenshots (not broken placeholders)

### 6.2 Report Results

Print:
1. Absolute path to `user-guide.pdf`
2. List of all pages/routes documented
3. Total number of screenshots captured
4. Any warnings (missing screenshots, skipped elements)

### 6.3 Cleanup (Optional)

The screenshots directory (`./user-guide-assets/screenshots/`) can be kept for reference or deleted after PDF generation. The manifest file can also be kept for reproducibility.

---

## Framework-Specific Notes

### Nuxt 3
- Routes are in `pages/` directory
- Dynamic routes use `[param].vue` syntax
- Middleware may redirect unauthenticated users
- Check `nuxt.config.ts` for custom route rules
- Default port: 3000

### Next.js
- Pages router: `pages/` directory
- App router: `app/` directory with `page.tsx` files
- API routes are NOT frontend pages (skip `/api/*`)
- Default port: 3000

### React (Vite/CRA)
- Routes typically in a router config file
- Look for `react-router-dom` imports
- Check `App.tsx` or dedicated routes file
- Default port: 5173 (Vite) or 3000 (CRA)

### Vue + Vue Router
- Routes in `src/router/index.ts`
- Components in `src/views/` or `src/pages/`
- Default port: 5173 (Vite) or 8080 (Vue CLI)

### SvelteKit
- Routes in `src/routes/` directory
- `+page.svelte` files are pages
- `+layout.svelte` for shared layouts
- Default port: 5173
