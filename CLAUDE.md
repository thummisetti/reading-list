# Reading List — Claude Context

## What This Is

A personal reading collection for Prakash Thummisetti — plain HTML files served via GitHub Pages at `thummisetti.github.io/reading-list/`. No frameworks, no build step, no CI. Push to `main` and it's live.

**Current topics:**
- `swe/` — Software engineering (FastAPI, API design, auth, patterns)
- `infra/` — Infrastructure and platform engineering (Terraform, AWS — in progress)
- `ppl/` — FAA Private Pilot License written exam prep (in progress)

---

## Tech Stack

- **Plain HTML + inline CSS only.** No external CSS files, no JavaScript frameworks, no npm, no build step.
- **Syntax highlighting:** [highlight.js](https://highlightjs.org/) loaded from CDN (`cdnjs.cloudflare.com`). Used in guide pages only, not index pages.
- **Fonts:** System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`) — no Google Fonts.
- **Deployment:** GitHub Pages, branch `main`, path `/`. Automatic on push.

---

## Directory Structure

```
reading-list/
├── index.html              ← Root landing page — topic cards
├── CLAUDE.md               ← This file
├── swe/
│   ├── index.html          ← SWE topic listing page
│   └── de-to-swe-guide.html
├── infra/
│   └── index.html          ← Placeholder until content is added
└── ppl/
    └── index.html          ← Placeholder until content is added
```

**Naming conventions:**
- Folder names: short, lowercase, no hyphens (e.g. `swe`, `ppl`, `infra`)
- Guide file names: `kebab-case.html` (e.g. `de-to-swe-guide.html`, `terraform-basics.html`)
- Every topic folder must have an `index.html`

---

## Design System

All pages share the same CSS variables. Copy these into every new page's `<style>` block:

```css
:root {
  --bg: #f9f8f6;
  --surface: #ffffff;
  --border: #e5e3df;
  --text: #1a1917;
  --text-muted: #6b6860;
  --accent: #2563eb;
  --accent-light: #dbeafe;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  --font-mono: "SF Mono", "Fira Code", "Cascadia Code", Consolas, monospace;
}
```

**Do not** introduce new colors, fonts, or design patterns without a good reason. Consistency across all guides is the point.

---

## Page Types & Templates

There are three page types. Match the right template for the job.

---

### Type 1: Root Landing Page (`index.html`)

Shows one card per topic. Cards link to `topic/index.html`.

**Card structure:**
```html
<a href="topic-folder/" class="card">
  <div class="card-icon">EMOJI</div>
  <div class="card-title">Topic Name</div>
  <div class="card-desc">One or two sentences describing what's in this section.</div>
  <div class="card-count">N guides</div>
</a>
```

Add `class="card soon"` for topics with no content yet (renders faded, non-clickable). Remove `soon` when the first guide is added.

**When to update:** Every time a new topic folder is created, add a card here. Update `card-count` when guides are added.

---

### Type 2: Topic Index Page (`topic/index.html`)

Lists all guides within a topic. Uses a breadcrumb nav back to root.

**Breadcrumb:**
```html
<nav class="breadcrumb">
  <a href="../">Reading List</a> &rsaquo; Topic Name
</nav>
```

**Guide list item structure:**
```html
<li class="guide-item">
  <a href="guide-filename.html">
    <span class="guide-icon">EMOJI</span>
    <div class="guide-body">
      <div class="guide-title">Guide Title</div>
      <div class="guide-desc">2–3 sentence description of what the guide covers.</div>
      <div class="guide-tags">
        <span class="tag">Tag1</span>
        <span class="tag">Tag2</span>
      </div>
    </div>
  </a>
</li>
```

**When to update:** Every time a new guide HTML file is added to the folder, add an entry here. Also update the `card-count` on the root `index.html`.

---

### Type 3: Guide Page (e.g. `swe/de-to-swe-guide.html`)

The actual reading content. Key structural elements:

**Head — include highlight.js for code blocks:**
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/json.min.js"></script>
<script>hljs.highlightAll();</script>
```

Add more language scripts as needed (e.g. `sql.min.js`, `bash.min.js`).

**Layout:** Two-column on desktop — sticky sidebar nav on the left, content on the right. Sidebar collapses on mobile (hidden via media query). See `swe/de-to-swe-guide.html` as the reference implementation.

**Callout box types** (use these, don't invent new ones):
```html
<div class="callout">General note</div>
<div class="callout warning">Watch-out / gotcha</div>
<div class="callout analogy">DE/domain analogy to aid understanding</div>
```

**Code file label** (above a code block, shows file path):
```html
<p class="code-label">path/to/file.py</p>
<pre><code class="language-python">...</code></pre>
```

**Flow diagrams** (for showing request flows, dependency chains, etc.):
```html
<div class="flow">
plain text diagram here
  └── with tree characters
</div>
```

**Content width:** Max `720px`, centered. Keep paragraphs tight — this is reference material, not a blog post.

**Sidebar nav:** The sidebar should have anchor links to every `<section id="...">` and major `<h3 id="...">` in the page. Include a scroll-spy script that highlights the active section (copy from the reference guide).

---

## Adding a New Guide

1. Write the HTML file in the appropriate topic folder
2. Add an entry to that topic's `index.html` guide list
3. Update the `card-count` in the root `index.html`
4. `git add . && git commit -m "..." && git push` — live in ~30 seconds

## Adding a New Topic

1. Create the folder: `mkdir topic-name`
2. Create `topic-name/index.html` using the Type 2 template (copy `infra/index.html` as a starting point)
3. Add a card to root `index.html` — start with `class="card soon"`, remove `soon` when first guide exists
4. Push

---

## What to Keep Out

- No JavaScript frameworks (React, Vue, Alpine, etc.)
- No CSS frameworks (Tailwind, Bootstrap, etc.)
- No external fonts
- No tracking scripts, analytics, or third-party embeds (except highlight.js for syntax highlighting)
- No `node_modules`, `package.json`, or any build tooling
- Company-internal code, credentials, or architecture details should be generalized before being included in guides
