# README Hero Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the top hero of `docs/local-preview.html` into a screenshot-oriented workflow demo that makes `Plan -> Work -> Review` legible within 3 seconds.

**Architecture:** Keep the work scoped to the existing static HTML preview page. Replace the current research-first hero with a composed workflow hero built from four visual zones: task input, workflow spine, execution result, and CLI evidence. Preserve the existing page below the fold so the hero can act as a reusable README/social screenshot surface without restructuring the whole page.

**Tech Stack:** Static HTML, inline CSS, semantic sections, local `python -m http.server` preview, manual browser verification.

---

### Task 1: Replace the hero content with a screenshot-oriented workflow composition

**Files:**
- Modify: `docs/local-preview.html`
- Test: `docs/local-preview.html`

- [ ] **Step 1: Run a failing content check for the new hero markers**

Run:

```powershell
Select-String -Path 'docs/local-preview.html' -Pattern 'A lightweight Agent Harness for structured engineering workflows','Task Input','Execution Result','Implement login flow'
```

Expected:

```text
No matches found for the new hero headline and workflow panel labels.
```

- [ ] **Step 2: Replace the existing hero section markup with the new four-zone hero**

Replace the current hero block beginning at `<section class="hero">` with this markup:

```html
    <section class="hero">
      <div class="eyebrow">Screenshot-ready workflow hero</div>
      <div class="hero-intro">
        <div class="hero-copy">
          <h1>A lightweight Agent Harness for structured engineering workflows</h1>
          <p>
            From task input to verdict output through a readable
            <strong>Plan - Work - Review</strong> loop.
          </p>
        </div>
        <div class="hero-actions">
          <a class="btn btn-primary" href="../harness-mvp/README.md">Open MVP Docs</a>
          <a class="btn btn-secondary" href="../research/README.md">Read the Research</a>
        </div>
      </div>

      <div class="hero-demo-grid">
        <article class="hero-stage hero-task">
          <div class="mini-tag">Task Input</div>
          <h2>Implement login flow</h2>
          <p class="hero-task-note">
            Start from a concrete engineering task instead of vague agent chat.
          </p>
          <div class="hero-meta">
            <span>Priority: <strong>REQUIRED</strong></span>
            <span>Effort: <strong>3</strong></span>
          </div>
          <ul class="hero-criteria">
            <li>Return 200 for valid credentials</li>
            <li>Issue a signed session token</li>
            <li>Handle invalid login with explicit feedback</li>
          </ul>
        </article>

        <article class="hero-stage hero-workflow">
          <div class="mini-tag">Workflow Spine</div>
          <div class="workflow-track">
            <div class="workflow-node">
              <span class="workflow-pill">Plan</span>
              <h3>Structure tasks and dependencies</h3>
              <p>Break the work into explicit units with acceptance criteria and execution context.</p>
            </div>
            <div class="workflow-arrow" aria-hidden="true">→</div>
            <div class="workflow-node">
              <span class="workflow-pill">Work</span>
              <h3>Execute in solo or parallel mode</h3>
              <p>Choose the smallest mode that gets the job done without adding unnecessary orchestration.</p>
            </div>
            <div class="workflow-arrow" aria-hidden="true">→</div>
            <div class="workflow-node">
              <span class="workflow-pill">Review</span>
              <h3>Return a verdict, not vague feedback</h3>
              <p>End with structured output that makes code quality and next action obvious.</p>
            </div>
          </div>
        </article>

        <article class="hero-stage hero-result">
          <div class="mini-tag">Execution Result</div>
          <div class="result-card">
            <span class="result-label">Mode</span>
            <strong>Solo</strong>
          </div>
          <div class="result-card">
            <span class="result-label">Task Status</span>
            <strong>DONE</strong>
          </div>
          <div class="result-card verdict-card">
            <span class="result-label">Verdict</span>
            <strong>APPROVE</strong>
            <small>0 critical · 0 major · 1 minor</small>
          </div>
        </article>
      </div>

      <div class="hero-cli-strip">
        <span class="cli-label">CLI Evidence</span>
        <code>harness plan add --title "Implement login flow" --priority REQUIRED</code>
        <code>harness work solo 1</code>
        <code>harness review code src/auth.py</code>
      </div>
    </section>
```

- [ ] **Step 3: Run a content check to verify the new hero copy is present**

Run:

```powershell
Select-String -Path 'docs/local-preview.html' -Pattern 'A lightweight Agent Harness for structured engineering workflows','Task Input','Execution Result','Implement login flow'
```

Expected:

```text
Matches are returned for the headline, task panel label, result panel label, and task title.
```

- [ ] **Step 4: Commit the hero markup rewrite**

```bash
git add docs/local-preview.html
git commit -m "feat: redesign preview hero around workflow demo"
```

### Task 2: Add hero-specific CSS for screenshot readiness and responsive readability

**Files:**
- Modify: `docs/local-preview.html`
- Test: `docs/local-preview.html`

- [ ] **Step 1: Run a failing CSS check for the new hero class names**

Run:

```powershell
Select-String -Path 'docs/local-preview.html' -Pattern '\.hero-demo-grid','\.workflow-track','\.hero-cli-strip','\.verdict-card'
```

Expected:

```text
No matches found for the new hero-specific CSS selectors.
```

- [ ] **Step 2: Add the new hero CSS rules near the existing `.hero` block**

Insert these rules after the current hero typography/action styles and before the existing section/card blocks:

```css
    .hero-intro {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 24px;
    }

    .hero-demo-grid {
      display: grid;
      grid-template-columns: minmax(260px, 0.9fr) minmax(0, 1.5fr) minmax(220px, 0.72fr);
      gap: 18px;
      margin-top: 28px;
    }

    .hero-stage {
      border-radius: 24px;
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255, 250, 242, 0.96) 0%, rgba(255, 253, 249, 0.92) 100%);
      padding: 22px;
      box-shadow: 0 12px 28px rgba(73, 52, 33, 0.08);
    }

    .hero-task h2,
    .hero-workflow h3,
    .hero-result strong {
      letter-spacing: -0.03em;
    }

    .hero-task h2 {
      margin: 0 0 10px;
      font-size: 1.55rem;
      line-height: 1.05;
    }

    .hero-task-note {
      margin: 0 0 16px;
      font-size: 0.96rem;
    }

    .hero-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 16px;
      font-size: 0.88rem;
      color: var(--muted);
    }

    .hero-meta span {
      padding: 8px 10px;
      border-radius: 999px;
      background: rgba(239, 213, 200, 0.45);
      border: 1px solid var(--line);
    }

    .hero-criteria {
      margin: 0;
      padding-left: 18px;
    }

    .hero-criteria li {
      margin: 8px 0;
    }

    .workflow-track {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 30px minmax(0, 1fr) 30px minmax(0, 1fr);
      gap: 8px;
      align-items: stretch;
      min-height: 100%;
    }

    .workflow-node {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 12px;
      padding: 16px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.65);
      border: 1px solid var(--line);
    }

    .workflow-pill {
      display: inline-flex;
      align-self: flex-start;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent-deep);
      font-size: 0.78rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    .workflow-node h3 {
      margin: 0;
      font-size: 1.1rem;
      line-height: 1.2;
    }

    .workflow-node p {
      margin: 0;
      font-size: 0.94rem;
    }

    .workflow-arrow {
      display: grid;
      place-items: center;
      color: var(--accent);
      font-size: 1.4rem;
      font-weight: bold;
    }

    .hero-result {
      display: grid;
      gap: 14px;
      align-content: start;
    }

    .result-card {
      padding: 16px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.66);
      border: 1px solid var(--line);
    }

    .result-label {
      display: block;
      margin-bottom: 8px;
      font-size: 0.8rem;
      color: var(--muted);
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    .result-card strong {
      display: block;
      font-size: 1.4rem;
      color: var(--ink);
    }

    .verdict-card strong {
      color: var(--green);
    }

    .verdict-card small {
      display: block;
      margin-top: 8px;
      color: var(--muted);
    }

    .hero-cli-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-top: 18px;
      padding: 14px 16px;
      border-radius: 18px;
      border: 1px solid rgba(255, 255, 255, 0.08);
      background: linear-gradient(180deg, #201c19 0%, #171412 100%);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    .hero-cli-strip .cli-label {
      color: #f1d4c4;
      font-size: 0.8rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    .hero-cli-strip code {
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
      color: #f3ede5;
      font-family: Consolas, "Courier New", monospace;
      font-size: 0.83rem;
      white-space: nowrap;
    }
```

- [ ] **Step 3: Update the responsive block so the hero still screenshots cleanly on smaller widths**

Inside the existing `@media (max-width: 1040px)` and `@media (max-width: 760px)` sections, add:

```css
      .hero-intro,
      .hero-demo-grid,
      .workflow-track {
        grid-template-columns: 1fr;
      }

      .hero-intro {
        align-items: start;
      }

      .workflow-arrow {
        transform: rotate(90deg);
        min-height: 18px;
      }
```

And inside the mobile block:

```css
      .hero-cli-strip {
        align-items: stretch;
      }

      .hero-cli-strip code {
        white-space: normal;
      }
```

- [ ] **Step 4: Run CSS/content verification after implementation**

Run:

```powershell
Select-String -Path 'docs/local-preview.html' -Pattern '\.hero-demo-grid','\.workflow-track','\.hero-cli-strip','\.verdict-card','A lightweight Agent Harness for structured engineering workflows'
```

Expected:

```text
Matches are returned for all new hero selectors and the new hero headline.
```

- [ ] **Step 5: Run the local preview server and visually verify the hero**

Run:

```powershell
& 'C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe' -m http.server 8123 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:8123/local-preview.html
```

Visual acceptance:

- the center workflow spine is the strongest visual anchor
- the left task input panel and right execution result panel are both visible without scrolling
- the CLI strip reads like evidence, not a second hero
- the hero can be screenshotted as a single frame for README use

- [ ] **Step 6: Commit the hero styling pass**

```bash
git add docs/local-preview.html
git commit -m "feat: style preview hero for README screenshot use"
```

### Task 3: Do a final screenshot-readiness pass against the approved spec

**Files:**
- Modify: `docs/local-preview.html`
- Reference: `docs/superpowers/specs/2026-07-02-readme-hero-demo-design.md`
- Test: `docs/local-preview.html`

- [ ] **Step 1: Compare the implemented hero against the design spec**

Check these spec points manually:

```text
- left panel shows task input
- center panel shows Plan -> Work -> Review
- right panel shows execution result
- bottom strip shows CLI evidence
- headline and support line match the approved copy direction
```

- [ ] **Step 2: Make any final copy tightening directly in the hero if needed**

If copy drift exists, the hero text should be normalized to:

```html
<h1>A lightweight Agent Harness for structured engineering workflows</h1>
<p>
  From task input to verdict output through a readable
  <strong>Plan - Work - Review</strong> loop.
</p>
```

- [ ] **Step 3: Run a final focused verification**

Run:

```powershell
Select-String -Path 'docs/local-preview.html' -Pattern 'Task Input','Workflow Spine','Execution Result','CLI Evidence','Plan - Work - Review'
```

Expected:

```text
All screenshot-critical labels are present exactly once in the hero.
```

- [ ] **Step 4: Commit the screenshot-readiness polish**

```bash
git add docs/local-preview.html
git commit -m "chore: polish hero screenshot copy and layout"
```

## Self-Review

### Spec coverage

- Hero goal covered by Tasks 1-3.
- Four-zone layout covered by Task 1 markup and Task 2 styling.
- Visual direction covered by Task 2 CSS.
- Copy direction covered by Tasks 1 and 3.
- Screenshot/readability acceptance covered by Tasks 2 and 3.

No spec gaps found.

### Placeholder scan

- No `TODO`, `TBD`, or deferred placeholders remain.
- All code-changing steps include concrete HTML or CSS blocks.
- All verification steps include exact commands and expected outcomes.

### Type consistency

- Hero class names are consistent across markup and CSS: `hero-demo-grid`, `workflow-track`, `hero-cli-strip`, `verdict-card`.
- Headline and support copy are repeated consistently in implementation and final polish steps.

Plan complete and saved to `docs/superpowers/plans/2026-07-02-readme-hero-demo.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
