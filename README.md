# ScenePack

`ScenePack` is the public-facing name for this project. It avoids the translation drift around `Peepaste` and gives the repository a cleaner external identity.

- Public name: `ScenePack`
- Internal codename: `Peepaste`
- Current Python package name: `peepaste`

## What This Project Actually Solves

This project is for people who work by pinning screenshots, arranging references, comparing UI states, collecting error messages, and then trying to continue the work with AI, docs, spreadsheets, or task tools.

The real problem is not "how to take one more screenshot". The real problem is:

> after people already spent effort arranging scattered material on the desktop, almost every downstream tool still asks them to explain everything again from scratch.

That repeated explanation is expensive. It burns attention, loses layout meaning, and makes AI handoff noisy.

`ScenePack` tries to preserve the user's desktop visual arrangement as structured project context before deeper reasoning begins.

## Why Existing Tools Still Leave A Gap

Current tools usually do one of these things well:

- capture screenshots
- pin images on the desktop
- store files
- run AI on individual images
- manage notes or tasks

But the working scene itself is usually lost:

- why these images are grouped together
- which items are central and which are reference-only
- what was compared side by side
- what stayed stable long enough to matter
- when the user was ready to name the scene and move forward

This project focuses on that missing layer.

## Product Positioning

`ScenePack` is not a screenshot tool replacement, and it is not pretending to be a universal AI agent.

It is a desktop visual aggregation layer:

- capture the scene quietly
- preserve layout and grouping signals
- wait for intent confirmation
- generate a clean handoff package
- let downstream AI or tools continue from better context

The current target environment is Windows desktop workflows, especially screenshot-heavy workbenches.

## Core Business Flow

The product spine is intentionally simple:

1. `Silent Capture`
   The monitor watches a stable desktop visual scene without interrupting the user.
2. `Needs Confirmation`
   The app shows the structure preview, candidate title, key references, risk, and whether deeper reading is needed.
3. `Ready To Handoff`
   After the title or intent is accepted, the app generates structured downstream files.
4. `Handed Off`
   The user copies or drags the package into an AI tool, document workflow, or another project system.
5. `Traceable Re-entry`
   The scene record remains available so the user can reopen, review, and continue without rebuilding context.

If this flow is not clear, the product fails. The current prototype is already organized around making that lifecycle visible.

## What Part Of The AI Chain We Are Optimizing

The recommended AI chain is:

`Scattered desktop materials -> stable visual scene -> structure capture -> human intent confirmation -> handoff package -> downstream model / agent / document flow -> review and iteration`

This project is not trying to optimize every link in that chain.

It is optimizing the first serious bottleneck:

> turning a messy, visual, partially organized working surface into a reusable context package with less repeated explanation.

In other words, the project works on the "pre-reasoning context formation" stage.

That stage is easy to underestimate, but in real work it is often where AI usage becomes slow, fragile, or annoying.

## Why The Need Starts Small But Can Expand

The initial demand is local and concrete:

- a designer comparing several UI references
- a PM sorting screenshots before writing a brief
- an engineer clustering bug screenshots and logs
- an operator collecting evidence for a recurring issue

At first, this looks like a narrow screenshot workflow problem.

But if the first-mile context becomes cleaner, the same mechanism can spread into broader workflows:

- AI briefing
- bug report generation
- research note packaging
- design review preparation
- product requirement drafting
- evidence-based task creation

Our working belief is not that "everything becomes ScenePack". It is narrower and more defensible:

> if the visual arrangement step is already part of someone's work, preserving that structure can improve many downstream outputs.

## If This Vision Does Not Fully Work

That outcome is acceptable, and it should be planned for honestly.

The fallback path is still useful:

- keep the product as a strong structured scene recorder
- focus on reliable export and review instead of ambitious auto-reasoning
- reduce AI dependence and let users edit the handoff manually
- narrow the supported workflow to screenshot-heavy desktop evidence packaging

If the broader expansion does not hold, the project can still survive as a focused productivity tool. That is a valid product outcome, not a failure in engineering terms.

## Current Prototype Status

The current prototype already has these meaningful pieces:

- Windows desktop tray-oriented workflow
- scene lifecycle visibility
- layout preview and structure-oriented metrics
- title confirmation before deeper generation
- generated handoff files such as `openclaw_prompt.md`, `review_sheet.md`, and `clipboard_bundle.txt`
- scene record reopening and downstream export actions
- language-linked interface switching between English and Chinese

The prototype is still early in these areas:

- stronger semantic understanding of scene content
- better generalization beyond the current Windows workflow
- production-grade robustness for long-running monitoring
- cleaner packaging and distribution discipline
- more evidence that downstream users consistently save time

## Technical Cost And Project Size Estimate

This is not a huge foundation-model project. It is a medium-complexity systems product with tricky UX and workflow details.

A realistic engineering view:

- Prototype to stable internal tool: roughly `4-8 engineer-weeks`
- Stable internal tool to public beta quality: roughly `2-4 engineer-months`
- Broader cross-workflow product with reliable AI integrations and stronger validation: roughly `6-12 engineer-months`

The time cost is driven less by algorithms alone and more by:

- Windows desktop capture reliability
- scene stability detection
- handoff package quality
- reviewable UX for confirmation states
- privacy boundaries
- downstream tool compatibility
- repeated user validation on real workflows

So the total workload is moderate in code size, but high in product precision. The hard part is not writing features quickly. The hard part is making the scene-to-context transition trustworthy.

## Practical Future Outlook

The future direction should stay engineering-led, not slogan-led.

Near-term worthwhile work:

- improve capture stability and scene deduplication
- make title acceptance and review signals clearer
- raise handoff package quality with fewer noisy fields
- validate one or two high-frequency workflows deeply

Mid-term worthwhile work:

- support richer downstream targets beyond one prompt bundle
- add selective AI reading only when the scene actually needs it
- compare package quality across different workflow types
- make manual correction easy when automatic inference is weak

Longer-term possibilities, only if the evidence supports them:

- scene-aware project memory
- multi-scene linkage for larger initiatives
- better task extraction from stable recurring layouts
- organization-grade evidence packaging for teams

The guardrail is simple:

> every expansion should prove that it removes repeated explanation work, not merely add more AI output.

## Naming Note

The repository and package can remain `peepaste` for compatibility during prototyping, but the public-facing copy should move toward `ScenePack` or another neutral brand in the same direction.

That lets the project keep engineering continuity without forcing the public story to inherit a bad translation outcome.

## Document Map

- [00 Product Definition](docs/00_product_definition.md)
- [01 MVP PRD](docs/01_mvp_prd.md)
- [02 Structure Pool](docs/02_structure_pool.md)
- [03 Record And Generation Rules](docs/03_record_and_generation_rules.md)
- [04 Dual Mode Intelligence](docs/04_dual_mode_intelligence.md)
- [05 Project Package Spec](docs/05_project_package_spec.md)
- [06 Naming And IP Guardrails](docs/06_naming_and_ip_guardrails.md)
- [07 Iteration Plan](docs/07_iteration_plan.md)
- [08 Architecture Standards](docs/08_architecture_standards.md)
- [09 V2 Validation Report](docs/09_v2_validation_report.md)
- [10 V2 Critical Audit](docs/10_v2_critical_audit.md)
- [12 Internal Test Installer](docs/12_internal_test_installer.md)
- [13 UX Handoff And Skill++ Decision](docs/13_ux_handoff_and_skill_plus_plus.md)

## Local Prototype Commands

Run tests:

```powershell
$env:PYTHONPATH="src"
py -m unittest discover -s tests
```

Run the record-state demo:

```powershell
$env:PYTHONPATH="src"
py -m peepaste demo
```

Accept a title and generate post-acceptance files:

```powershell
$env:PYTHONPATH="src"
py -m peepaste accept-title .peepaste-runs\demo --title "Accepted Visual Scene" --generate
```

Capture visible Snipaste-oriented windows:

```powershell
$env:PYTHONPATH="src"
py -m peepaste capture-windows --process Snipaste
```

Capture only Snipaste pinned-image windows:

```powershell
$env:PYTHONPATH="src"
py -m peepaste capture-windows --process Snipaste --snipaste-pasters-only
```

Create or inspect local settings:

```powershell
$env:PYTHONPATH="src"
py -m peepaste settings init
py -m peepaste settings show
```

Initialize internal test settings:

```powershell
$env:PYTHONPATH="src"
py -m peepaste init --storage-root ".peepaste-runs\projects" --language en --theme light
```

Monitor Snipaste pinned-image changes:

```powershell
$env:PYTHONPATH="src"
py -m peepaste monitor-snipaste --iterations 5 --interval 1.5 --stable-ticks 2
```

Start the optional tray UI after installing GUI dependencies:

```powershell
py -m pip install -e .[gui]
peepaste gui
```

Build the internal Windows test package:

```powershell
.\tools\build_internal_package.ps1
```

Run only the packaged release output:

```text
dist\ScenePack\ScenePack.exe
dist\ScenePack-0.3.0-internal-win64\ScenePack.exe
```

Do not run `build\peepaste_internal\ScenePack.exe`. The `build` folder is only PyInstaller work output and can fail with `Error loading Python DLL`.

Current internal package output:

```text
dist\ScenePack-0.3.0-internal-win64.zip
```
