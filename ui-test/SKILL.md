---
name: ui-test
description: "AI-powered adversarial UI testing via the browse CLI. Analyzes git diffs to test only what changed, or explores the full app to find bugs. Tests functional correctness, accessibility, responsive layout, and UX heuristics. Use when the user asks to test UI changes, QA a pull request, audit accessibility, or run exploratory testing. Supports local browser (localhost) and remote Browserbase (deployed sites)."
license: MIT
metadata:
  author: browserbase
  version: "0.4.0"
compatibility: "Requires the browse CLI (`npm install -g @browserbasehq/browse-cli`). For remote testing: BROWSERBASE_API_KEY and cookie-sync skill."
---

# UI Test - Browserbase UI Testing Skill

Test UI changes in a real browser. Your job is to **try to break things**, not confirm they work.

Three workflows:
- **Diff-driven** 鈥?analyze a git diff, test only what changed
- **Exploratory** 鈥?navigate the app, find bugs the developer didn't think about
- **Parallel** - fan out independent test groups across multiple Browserbase browsers when the user explicitly asks for sub-agents or parallel agent work

## How Testing Works

Codex coordinates the test strategy, runs the relevant `browse` commands, and reports findings. Use Codex sub-agents only when the user explicitly asks for sub-agents, delegation, or parallel agent work.

### Planning: multiple angles, then execute once

Complete the three planning rounds before execution. Keep the plan concise unless the user asked for a detailed QA plan.

**Round 1 鈥?Functional:** What are the core user flows? What should work? Write out each test as: action 鈫?expected result.

**Round 2 鈥?Adversarial:** Re-read Round 1. What did you miss? Think about: different user types/roles, error paths, empty states, race conditions, edge inputs (empty, huge, special chars, rapid clicks).

**Round 3 鈥?Coverage gaps:** Re-read Rounds 1鈥?. What about: accessibility (axe-core, keyboard-only), mobile viewports, console errors, visual consistency with the rest of the app?

**Deduplicate:** Merge all three rounds into one numbered list of tests. Remove overlaps. Assign each test to a group (e.g. Group A, Group B).

Then execute the highest-value checks. If the user explicitly requested parallel agents, launch one sub-agent per group; otherwise run the checks directly with the `browse` CLI.

When using sub-agents, output the three rounds, the merged plan, and the group assignments before spawning agents.

### Principles for splitting work

- **Sub-agents run assigned tests, not open exploration.** When sub-agents are explicitly requested, hand each one a specific numbered list of tests. They execute the list and stop.
- **The bottleneck is the slowest agent** 鈥?split work so no single agent has a disproportionate share. Many small agents > few large ones.
- **Size the effort to the change** 鈥?a single component fix doesn't need many agents or many steps. A full-page redesign does. Let the scope of the diff drive the plan.
- **No early stopping on failures** 鈥?find as many bugs as possible within the assigned tests.

### Giving sub-agents a step budget

When using sub-agents, include an explicit browse step limit in every sub-agent prompt.

As a rough heuristic: ~25 steps for a few targeted checks, ~40 for a full page with functional + adversarial + a11y, ~75 for multiple pages or a broad category. **Adjust based on what the assigned tests actually require** 鈥?these are starting points, not rules.

As a rough heuristic: ~25 steps for a few targeted checks, ~40 for a full page with functional + adversarial + a11y, ~75 for multiple pages or a broad category. **Adjust based on what the assigned tests actually require** 鈥?these are starting points, not rules.

Every sub-agent prompt must include:
```
You have a budget of N browse steps (each `browse` command = 1 step). Count your steps as you go. When you reach N, stop immediately and report:
- STEP_PASS/STEP_FAIL for every test you completed
- STEP_SKIP|<test-id>|budget reached for every test you didn't get to

Do not retry or continue after hitting the budget.
Run only these tests: [numbered list from the merged plan]
Do not explore beyond the assigned tests.
Do NOT generate an HTML report or write any files. Return only step markers and your findings as text.
```

Without explicit sub-agent authorization, Codex should run `browse` commands itself.

**When a sub-agent hits its budget, the main agent accepts the partial results as-is.** Do not re-run or retry the sub-agent. Include SKIPPED tests in the final report so the developer knows what wasn't covered.

### Reporting

**Every sub-agent reports back with:**
```
Tests: 8 | Passed: 5 | Failed: 2 | Skipped: 1 | Pages visited: 2
```

**The main agent merges into a final report with:**
```
Tests: 20 | Passed: 14 | Failed: 4 | Skipped: 2 | Agents: 3 | Pass rate: 70%
```

Do not report "steps used" 鈥?browse command counts are implementation plumbing, not a meaningful metric for reviewers.

## Testing Philosophy

**You are an adversarial tester.** Your goal is to find bugs, not prove correctness.

- **Try to break every feature you test.** Don't just check "does the button exist?" 鈥?click it twice rapidly, submit empty forms, paste 500 characters, press Escape mid-flow.
- **Test what the developer didn't think about.** Empty states, error recovery, keyboard-only navigation, mobile overflow.
- **Every assertion must be evidence-based.** Compare before/after snapshots. Check specific elements by ref. Never report PASS without concrete evidence from the accessibility tree or a deterministic check.
- **Report failures with enough detail to reproduce.** Include the exact action, what you expected, what you got, and a suggested fix.

## Assertion Protocol

Every test step MUST produce a structured assertion. Do not write freeform "this looks good."

### Step markers

For each test step, emit exactly one marker:

```
STEP_PASS|<step-id>|<evidence>
```
or
```
STEP_FAIL|<step-id>|<expected> 鈫?<actual>|<screenshot-path>
```

- `step-id`: short identifier like `homepage-cta`, `form-validation-error`, `modal-cancel`
- `evidence`: what you observed that proves the step passed (element ref, text content, URL, eval result)
- `expected 鈫?actual`: what you expected vs what you got
- `screenshot-path`: path to the saved screenshot (failures only 鈥?see Screenshot Capture below)

### Screenshot Capture for Failures

**Every STEP_FAIL MUST have an accompanying screenshot** so the developer can see what went wrong visually.

When a test step fails:

```bash
# 1. Take a screenshot immediately after observing the failure
browse screenshot --path .context/ui-test-screenshots/<step-id>.png

# If --path is not supported, take the screenshot and save manually:
browse screenshot
# The browse CLI will output the screenshot path 鈥?move/copy it:
cp /tmp/browse-screenshot-*.png .context/ui-test-screenshots/<step-id>.png
```

Setup the screenshot directory at the start of any test run:

```bash
mkdir -p .context/ui-test-screenshots
```

**Rules:**
- File name = step-id (e.g., `double-submit.png`, `axe-audit.png`, `modal-focus-trap.png`)
- Store in `.context/ui-test-screenshots/` 鈥?this directory is gitignored and accessible to the developer and other agents
- For parallel runs, include the session name: `<session>-<step-id>.png` (e.g., `signup-double-submit.png`)
- Take the screenshot at the moment of failure 鈥?capture the broken state, not after recovery
- For visual/layout bugs, also screenshot the baseline (working state) for comparison: `<step-id>-baseline.png`

### How to verify (in order of rigor)

1. **Deterministic check** (strongest) 鈥?`browse eval` returns structured data you can inspect. Examples: axe-core violation count, `document.title`, form field value, console error array, element count.
2. **Snapshot element match** 鈥?a specific element with a specific role and text exists in the accessibility tree. Check by ref: `@0-12 button "Save"`. An element either exists in the tree or it doesn't.
3. **Before/after comparison** 鈥?snapshot before action, act, snapshot after. Verify the tree changed in the expected way (element appeared, disappeared, text changed).
4. **Screenshot + visual judgment** (weakest) 鈥?only for visual-only properties (color, spacing, layout) that the accessibility tree cannot capture. Always accompany with what specifically you're evaluating.

### Before/after comparison pattern

This is the core verification loop. Use it for every interaction:

```bash
# 1. BEFORE: capture state
browse snapshot
# Record: what elements exist, their text, their refs

# 2. ACT: perform the interaction
browse click @0-12

# 3. AFTER: capture new state
browse snapshot
# Compare: what changed? What appeared? What disappeared?

# 4. ASSERT: emit marker based on comparison
# If dialog appeared: STEP_PASS|modal-open|dialog "Confirm" appeared at @0-20
# If nothing changed:
browse screenshot --path .context/ui-test-screenshots/modal-open.png
# STEP_FAIL|modal-open|expected dialog to appear 鈫?snapshot unchanged|.context/ui-test-screenshots/modal-open.png
```

## Setup

```bash
which browse || npm install -g @browserbasehq/browse-cli
```

### Avoid permission fatigue

This skill runs many `browse` commands (snapshots, clicks, evals). To avoid approving each one, add `browse` to your allowed commands:

Add both patterns to `.codex/settings.json` (project-level) or `~/.codex/settings.json` (user-level) when your Codex environment supports command allowlists:
```json
{
  "permissions": {
    "allow": [
      "Bash(browse:*)",
      "Bash(BROWSE_SESSION=*)"
    ]
  }
}
```

The first pattern covers plain `browse` commands. The second covers parallel sessions (`BROWSE_SESSION=signup browse open ...`). Both are needed to avoid approval prompts.

## Mode Selection

| Target | Mode | Command | Auth |
|--------|------|---------|------|
| `localhost` / `127.0.0.1` | Local | `browse env local` | None needed (clean isolated local browser by default) |
| Deployed/staging site | Remote | `browse env remote` | cookie-sync 鈫?`--context-id` |

**Rule: If the target URL contains `localhost` or `127.0.0.1`, always use `browse env local`.**

### Local Mode (default for localhost)

```bash
browse env local
browse open http://localhost:3000
```

`browse env local` uses a clean isolated local browser by default, which is best for reproducible localhost QA runs.

Use local-mode variants only when needed:

- `browse env local --auto-connect` 鈥?auto-discover existing local Chrome, fallback to isolated. Use this only when the test explicitly needs existing local login/cookies/state.
- `browse env local <port|url>` 鈥?attach to a specific CDP target (explicit local browser attach).

### Remote Mode (deployed sites via cookie-sync)

```bash
# Step 1: Sync cookies from local Chrome to Browserbase
node .codex/skills/cookie-sync/scripts/cookie-sync.mjs --domains your-app.com
# Output: Context ID: ctx_abc123

# Step 2: Switch to remote mode
browse env remote
browse open https://staging.your-app.com --context-id ctx_abc123 --persist
browse snapshot
# ... run tests ...
browse stop
```

Cookie-sync flags: `--domains`, `--context`, `--stealth`, `--proxy "City,ST,US"`

## Workflow A: Diff-Driven Testing

### Phase 1: Analyze the diff

```bash
git diff --name-only HEAD~1          # or: git diff --name-only / git diff --name-only main...HEAD
git diff HEAD~1 -- <file>            # read actual changes
```

Categorize changed files:

| File pattern | UI impact | What to test |
|-------------|-----------|--------------|
| `*.tsx`, `*.jsx`, `*.vue`, `*.svelte` | Component | Render, interaction, state, edge cases |
| `pages/**`, `app/**`, `src/routes/**` | Route/page | Navigation, page load, content, 404 handling |
| `*.css`, `*.scss`, `*.module.css` | Style | Visual appearance (screenshot), responsive |
| `*form*`, `*input*`, `*field*` | Form | Validation, submission, empty input, long input, special chars |
| `*modal*`, `*dialog*`, `*dropdown*` | Interactive | Open/close, escape, focus trap, cancel vs confirm |
| `*nav*`, `*menu*`, `*header*` | Navigation | Links, active states, routing, keyboard nav |
| Non-UI files only | None | Skip 鈥?report "no UI tests needed" |

### Phase 2: Map files to URLs

Detect framework: `cat package.json | grep -E '"(next|react|vue|nuxt|svelte|@sveltejs|angular|vite)"'`

| Framework | Default port | File 鈫?URL pattern |
|-----------|-------------|-----|
| Next.js App Router | 3000 | `app/dashboard/page.tsx` 鈫?`/dashboard` |
| Next.js Pages Router | 3000 | `pages/about.tsx` 鈫?`/about` |
| Vite | 5173 | Check router config |
| Nuxt | 3000 | `pages/index.vue` 鈫?`/` |
| SvelteKit | 5173 | `src/routes/+page.svelte` 鈫?`/` |
| Angular | 4200 | Check routing module |

### Phase 3: Ensure the right code is running

Before testing, verify the dev server is serving the code from the diff 鈥?not a stale branch.

**If testing a PR or specific branch:**
```bash
# Check what branch is currently checked out
git branch --show-current

# If it's not the PR branch, switch to it
git fetch origin <branch> && git checkout <branch>

# Install deps 鈥?the lockfile may differ between branches
yarn install  # or npm install / pnpm install
```

If the dev server was already running on a different branch, restart it after checkout.

**Find a running dev server:**
```bash
for port in 3000 3001 5173 4200 8080 8000 5000; do
  s=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" 2>/dev/null)
  if [ "$s" != "000" ]; then echo "Dev server on port $port (HTTP $s)"; fi
done
```

If nothing found: tell the user to start their dev server.

**Verify it actually renders:**
After `browse open` + `browse snapshot`, check that the accessibility tree contains real page content (navigation, headings, interactive elements) 鈥?not just an error overlay or empty body. Next.js dev servers can return HTTP 200 while showing a full-screen build error dialog. If the snapshot is empty or dominated by an error dialog, the server is broken 鈥?fix the build before testing.

### Phase 4: Generate test plan

For each changed area, plan **both happy path AND adversarial tests**:

```
Test Plan (based on git diff)
=============================
Changed: src/components/SignupForm.tsx (added email validation)

1. [happy] Valid email submits successfully
   URL: http://localhost:3000/signup
   Steps: fill valid email 鈫?submit 鈫?verify success message appears

2. [adversarial] Invalid email shows error
   Steps: fill "not-an-email" 鈫?submit 鈫?verify error message appears

3. [adversarial] Empty form submission
   Steps: click submit without filling anything 鈫?verify error, no crash

4. [adversarial] XSS in email field
   Steps: fill "<script>alert(1)</script>" 鈫?submit 鈫?verify sanitized/rejected

5. [adversarial] Rapid double-submit
   Steps: click submit twice quickly 鈫?verify no duplicate submission

6. [adversarial] Keyboard-only flow
   Steps: Tab to email 鈫?type 鈫?Tab to submit 鈫?Enter 鈫?verify success
```

### Phase 5: Execute tests

```bash
browse stop 2>/dev/null
mkdir -p .context/ui-test-screenshots
# localhost/default QA 鈫?clean, reproducible local run
browse env local
```

For each test, follow the **before/after pattern**:

```bash
# Navigate
browse open http://localhost:3000/path
browse wait load

# BEFORE snapshot
browse snapshot
# Note the current state: elements, refs, text

# ACT
browse click @0-ref
# or: browse fill "selector" "value"
# or: browse type "text"
# or: browse press Enter

# AFTER snapshot
browse snapshot
# Compare against BEFORE: what changed?

# ASSERT with marker
# STEP_PASS|step-id|evidence  OR  STEP_FAIL|step-id|expected 鈫?actual
```

### Phase 6: Report results

```
## UI Test Results

### STEP_PASS|valid-email-submit|status "Thanks!" appeared at @0-42 after submit
- URL: http://localhost:3000/signup
- Before: form with email input @0-3, submit button @0-7
- Action: filled "user@test.com", clicked @0-7
- After: form replaced by status element with "Thanks! We'll be in touch."

### STEP_FAIL|double-submit|expected single submission 鈫?form submitted twice|.context/ui-test-screenshots/double-submit.png
- URL: http://localhost:3000/signup
- Before: form with submit button @0-7
- Action: clicked @0-7 twice rapidly
- After: two success toasts appeared, suggesting duplicate submission
- Screenshot: .context/ui-test-screenshots/double-submit.png
- Suggestion: disable submit button after first click, or debounce the handler

---
**Summary: 4/6 passed, 2 failed**
Failed: double-submit, xss-sanitization

Screenshots saved to `.context/ui-test-screenshots/` 鈥?open any failed step's screenshot to see the broken state.
```

Always `browse stop` when done.

### Phase 7: Generate HTML report

After producing the text report, generate a standalone HTML report that a reviewer can open in a browser. The report embeds screenshots inline (base64) so it works as a single file 鈥?no external dependencies.

**Why:** Text reports are good for the agent conversation, but reviewers (PMs, designers, other engineers) want a visual artifact they can open, scan, and share. Screenshots inline make failures immediately obvious.

#### How to generate

1. Read the HTML template at [references/report-template.html](references/report-template.html)
2. Build the report by replacing the template placeholders with actual test data:

| Placeholder | Value |
|-------------|-------|
| `{{TITLE}}` | Report title for `<title>` tag (e.g., "UI Test: PR #1234 鈥?OAuth Settings") |
| `{{TITLE_HTML}}` | Report title for the visible `<h1>`. If a PR URL is available, wrap the PR reference in an `<a>` tag so it's clickable (e.g., `UI Test: <a href="https://github.com/org/repo/pull/1234">PR #1234</a> 鈥?OAuth Settings`). If no URL, use plain text same as `{{TITLE}}`. |
| `{{META}}` | One-line context: date, app URL, user, branch |
| `{{TOTAL_TESTS}}` | Total STEP_PASS + STEP_FAIL count |
| `{{AGENT_COUNT}}` | Number of sub-agents that ran |
| `{{PASS_COUNT}}` | Number of STEP_PASS |
| `{{FAIL_COUNT}}` | Number of STEP_FAIL |
| `{{PASS_RATE}}` | Integer percentage (e.g., "92") |
| `{{RATE_CLASS}}` | `good` (鈮?0%), `warn` (70鈥?9%), `bad` (<70%) |
| `{{FAILURES_SECTION}}` | HTML for failed test cards (see below) |
| `{{PASSES_SECTION}}` | HTML for passed test cards (see below) |

3. For each test result, generate a `<details>` card. Failed tests should be **open by default** so reviewers see them immediately:

```html
<!-- Failed test card (open by default) -->
<div class="section">
  <h2>Failures <span class="count">{{FAIL_COUNT}}</span></h2>
  <details class="test-card fail" open>
    <summary>
      <span class="badge fail">FAIL</span>
      <span class="step-id">step-id-here</span>
      <span class="evidence">expected 鈫?actual</span>
    </summary>
    <div class="body">
      <dl>
        <dt>URL</dt><dd>http://localhost:3000/path</dd>
        <dt>Action</dt><dd>What was done</dd>
        <dt>Expected</dt><dd>What should have happened</dd>
        <dt>Actual</dt><dd>What happened instead</dd>
      </dl>
      <div class="suggestion">Fix: description of suggested fix</div>
      <div class="screenshot">
        <img src="data:image/png;base64,..." alt="Screenshot of failure">
        <div class="caption">step-id.png 鈥?captured at moment of failure</div>
      </div>
    </div>
  </details>
</div>

<!-- Passed test card (collapsed by default) -->
<div class="section">
  <h2>Passed <span class="count">{{PASS_COUNT}}</span></h2>
  <details class="test-card pass">
    <summary>
      <span class="badge pass">PASS</span>
      <span class="step-id">step-id-here</span>
      <span class="evidence">evidence summary</span>
    </summary>
    <div class="body">
      <dl>
        <dt>URL</dt><dd>http://localhost:3000/path</dd>
        <dt>Evidence</dt><dd>What was observed</dd>
      </dl>
    </div>
  </details>
</div>
```

4. **Embed screenshots as base64** so the HTML is fully self-contained:

```bash
# Convert screenshot to base64 data URI
base64 -i .context/ui-test-screenshots/step-id.png | tr -d '\n'
# Use as: src="data:image/png;base64,<output>"
```

Read each screenshot file referenced in STEP_FAIL markers, base64-encode it, and embed it as an `<img src="data:image/png;base64,...">` in the corresponding test card. For STEP_PASS, only embed a screenshot if one was explicitly taken (e.g., baseline screenshots).

5. Write the final HTML to `.context/ui-test-report.html`:

```bash
# Write the generated HTML
cat > .context/ui-test-report.html << 'REPORT_EOF'
<!DOCTYPE html>
...generated report...
REPORT_EOF

# Open it for the reviewer
open .context/ui-test-report.html  # macOS
# xdg-open .context/ui-test-report.html  # Linux
```

6. Tell the user: `Report saved to .context/ui-test-report.html` and offer to open it.

**Rules:**
- Failures section comes before passes 鈥?reviewers care about what's broken first
- Failed cards are `open` by default; passed cards are collapsed
- Every STEP_FAIL card MUST have an embedded screenshot 鈥?if the screenshot file is missing, note it in the card
- Include the suggestion/fix in each failure card if one was provided
- The report must work offline 鈥?no CDN links, no external assets
- Keep the HTML under 5MB 鈥?if screenshots push it over, reduce image quality or skip baseline screenshots for passes

## Adversarial Test Patterns

Apply these to every interactive element you test. Read [references/adversarial-patterns.md](references/adversarial-patterns.md) for the full pattern library (forms, modals, navigation, error states, keyboard accessibility).

## Deterministic Checks

These produce structured data, not judgment calls. Use them as the strongest form of assertion.

| Check | What it catches | Assertion |
|-------|----------------|-----------|
| axe-core | WCAG violations | `violations.length === 0` |
| Console errors | Runtime exceptions, failed requests | empty error array |
| Broken images | Missing/failed image loads | no images with `naturalWidth === 0` |
| Form labels | Inputs without accessible labels | every input has `hasLabel: true` |

For the exact `browse eval` recipes, read [references/browser-recipes.md](references/browser-recipes.md).

## Workflow B: Exploratory Testing

No diff, no plan 鈥?just open the app and try to break it. Use this when the user says "test my app", "find bugs", or "QA this site."

### Approach

1. **Discover the app** 鈥?read `package.json` to detect the framework, then open the root URL and snapshot to see what's there
2. **Navigate everything** 鈥?click through nav links, visit every reachable page, note what exists
3. **Test what you find** 鈥?for each page, apply the adversarial patterns below (forms, modals, navigation, keyboard, error states)
4. **Run deterministic checks** 鈥?axe-core, console errors, broken images, form labels on every page
5. **Report findings** 鈥?use STEP_PASS/STEP_FAIL markers, include reproduction steps for failures

Don't try to be systematic about coverage. Just explore like a user would, but with the intent to break things. The agent is good at this 鈥?let it roam.

### Tips for exploratory runs

- Start with the homepage, then follow the navigation naturally
- Try the 404 page (`/does-not-exist`) 鈥?is it custom or default?
- Look for empty states (pages with no data)
- Test forms with garbage input before valid input
- Check mobile viewport (375px) on every page 鈥?does it overflow?
- If the app has auth, use cookie-sync first

## Workflow C: Parallel Testing

Run independent test groups concurrently using named `browse` sessions (`BROWSE_SESSION=<name>`). Each session gets its own browser. Works with both local and remote mode.

Use when testing multiple pages or categories and you want faster wall clock time.

Read [references/parallel-testing.md](references/parallel-testing.md) for the full workflow: session setup, agent fan-out, cookie-sync for auth, and result merging.

## Design Consistency

Check whether changed UI matches the rest of the app visually. Read [references/design-consistency.md](references/design-consistency.md) when doing visual or design checks.

## Test Categories

| Category | How | Assertion type |
|----------|-----|---------------|
| Accessibility | axe-core + keyboard nav | Deterministic (violation count) |
| Visual Quality | Screenshot + heuristic evaluation | Visual judgment (weakest 鈥?note specifics) |
| Responsive | Viewport sweep + screenshots | Visual + deterministic (overflow check) |
| Console Health | Console capture eval | Deterministic (error count) |
| UX Heuristics | Snapshot + Laws of UX + Nielsen's | Structured judgment (cite specific heuristic) |
| Error States | Navigate to empty/error states | Before/after comparison |
| Data Display | Snapshot on tables/dashboards | Element match (column count, formatting) |
| Design Consistency | Screenshot baseline + changed page comparison | Visual judgment (cite specific property) |
| Exploratory | Free navigation + adversarial testing | Before/after + judgment |

Reference guides (load on demand):
- **Adversarial patterns** 鈥?[references/adversarial-patterns.md](references/adversarial-patterns.md) 鈥?load when testing forms, modals, navigation, or keyboard a11y
- **Browser recipes** 鈥?[references/browser-recipes.md](references/browser-recipes.md) 鈥?load when running deterministic checks (axe-core, console, images, form labels)
- **Exploratory testing** 鈥?[references/exploratory-testing.md](references/exploratory-testing.md) 鈥?load for Workflow B (no diff, open exploration)
- **UX heuristics** 鈥?[references/ux-heuristics.md](references/ux-heuristics.md) 鈥?load when evaluating UX quality or citing specific heuristics
- **Design system** 鈥?[references/design-system.example.md](references/design-system.example.md) 鈥?template for users to customize
- **Design consistency** 鈥?[references/design-consistency.md](references/design-consistency.md) 鈥?load when doing visual consistency checks
- **Parallel testing** 鈥?[references/parallel-testing.md](references/parallel-testing.md) 鈥?load for Workflow C (concurrent sessions)
- **Report template** 鈥?[references/report-template.html](references/report-template.html) 鈥?HTML template for Phase 7 report generation

For worked examples with exact commands, read [EXAMPLES.md](EXAMPLES.md) if you need to see the assertion protocol in action.

## Best Practices

1. **Be adversarial** 鈥?try to break things, don't just confirm they work
2. **Every assertion needs evidence** 鈥?snapshot ref, eval result, or before/after diff
3. **Before/after for every interaction** 鈥?snapshot, act, snapshot, compare
4. **Screenshot every failure** 鈥?`browse screenshot` immediately on STEP_FAIL, save to `.context/ui-test-screenshots/<step-id>.png`
5. **Deterministic checks first** 鈥?axe-core, console errors, form labels before visual judgment
6. **For localhost, start with clean local mode** 鈥?use `browse env local` first for reproducible runs; use `--auto-connect` only when existing local state is required
7. **Always `browse stop` when done** 鈥?for parallel runs, stop every named session
8. **Report failures with reproduction steps** 鈥?action, expected, actual, screenshot path, suggestion
9. **Parallelize independent tests** 鈥?use Workflow C with named sessions when testing multiple pages or categories on a deployed site

## Troubleshooting

- **"No active page"**: `browse stop`, retry. For zombies: `pkill -f "browse.*daemon"`
- **Dev server not responding**: `curl http://localhost:<port>` 鈥?ask user to start it
- **`browse eval` with `await` fails**: Use `.then()` instead 鈥?`browse eval` doesn't support top-level await
- **Element ref not found**: `browse snapshot` again 鈥?refs change on page update
- **Blank snapshot**: `browse wait load` or `browse wait selector ".expected"` before snapshotting
- **SPA deep links 404**: Navigate to `/` first, then click through
- **Remote auth fails**: Re-run cookie-sync with `--context <id>`, try `--stealth`
- **Parallel session conflicts**: Ensure every `browse` command uses `BROWSE_SESSION=<name>` 鈥?without it, commands go to the default session
- **Session not stopping**: `BROWSE_SESSION=<name> browse stop`. For zombies: `pkill -f "browse.*<name>.*daemon"`
