# README Hero Demo Design

## Goal

Create a single screenshot-oriented hero section for `docs/local-preview.html` that can later be reused as:

- the lead visual for the repository README
- a social preview screenshot
- a fast explanation of what the project does in under 3 seconds

The hero should prioritize **workflow clarity** over feature breadth.

## Core Message

The screenshot should communicate one idea first:

`Harness Engineering Study turns engineering tasks into a structured Plan -> Work -> Review workflow.`

Secondary ideas:

- this is a runnable Agent Harness MVP
- this is for real engineering tasks, not vague agent chat
- the output is structured and reviewable

## Recommended Layout

Use a single wide hero composition with four zones:

### 1. Left panel: Task Input

Purpose:
Show that the system begins with a real engineering task.

Content:

- task title such as `Implement login flow`
- priority such as `REQUIRED`
- 2-3 acceptance criteria
- a short note that the task is concrete and engineering-oriented

### 2. Center panel: Workflow Spine

Purpose:
Be the visual anchor of the entire screenshot.

Content:

- `Plan`
- `Work`
- `Review`

Each step gets one short explanation:

- `Plan: structure tasks and dependencies`
- `Work: execute in solo or parallel mode`
- `Review: return a verdict, not vague feedback`

This section should be the largest and most visually dominant part of the hero.

### 3. Right panel: Execution Result

Purpose:
Prove that the workflow ends in a concrete result.

Content:

- `Mode: Solo`
- `Task Status: DONE`
- `Verdict: APPROVE`

Optional supporting signal:

- `0 critical`
- `0 major`
- `1 minor`

### 4. Bottom strip: CLI Evidence

Purpose:
Prevent the hero from feeling like a conceptual diagram only.

Content:

```bash
harness plan add --title "Implement login flow" --priority REQUIRED
harness work solo 1
harness review code src/auth.py
```

This strip should look like a lightweight terminal ribbon, not a full terminal block.

## Visual Direction

Preferred direction:

- engineering console feel
- structured and tool-like
- warm paper background with dark ink text and orange highlight accents
- clear hierarchy without becoming a SaaS marketing landing page

Avoid:

- overly abstract diagram styling
- feature grid overload
- decorative elements that compete with the workflow spine
- generic dark terminal mockups that hide the repo's differentiated visual language

## Copy Direction

Hero headline:

`A lightweight Agent Harness for structured engineering workflows`

Support line:

`From task input to verdict output through a readable Plan -> Work -> Review loop.`

## Acceptance Criteria

The hero is successful if:

1. A first-time visitor can identify `Plan -> Work -> Review` within 3 seconds.
2. The page looks like an engineering tool surface rather than a generic AI landing page.
3. The left and right panels make the workflow feel grounded in inputs and outputs.
4. The hero can be screenshotted cleanly for README or social sharing without requiring scrolling.
5. The updated hero still fits naturally inside the broader `docs/local-preview.html` page.

## Implementation Scope

This design only covers the top hero section of `docs/local-preview.html`.

It does not yet include:

- extra social variants
- a dedicated Open Graph image
- README image embedding
- multiple screenshot compositions
