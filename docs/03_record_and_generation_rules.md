# Record And Generation Rules / 记录与后置生成规则

Version: v0.1

## Core Rule

Record first, generate later.

中文：

先结构记录，后标题命中，最后再推演生成。

## Default No-Response Bypass

The default bypass is not a hidden AI action. It is a quiet capture loop:

- monitor the configured desktop source
- detect layout changes
- wait for a stable scene
- write a scene record once per stable fingerprint
- show status in the GUI without blocking the user's work

The bypass must not:

- infer final semantic meaning
- generate project files
- submit anything to downstream tools
- read or upload image content without explicit permission

## Immediate Record

After a capture event, ScenePack may immediately save:

- `timestamp`
- `layout_snapshot`
- `structure_pool_hits`
- `layout_message`
- `title_candidates`
- `capture_source`
- `privacy_state`
- `mode_state`

This is allowed because it preserves the scene without pretending to know the final project meaning.

## Layout Message

The layout message should be short and structural.

Example:

```text
Captured 18 items. The scene contains 3 visible zones, 1 dense pool, 2 isolated items, and 1 possible attention anchor. Title confidence is low.
```

中文示例：

```text
已捕获 18 个项目。当前现场包含 3 个可见区域、1 个密集池、2 个孤立项和 1 个可能的注意力锚点。标题置信度较低。
```

## Title Candidate

A title candidate can be generated early, but it is not yet a project truth.

Title candidate sources:

- user typed text
- repeated scene structure
- folder or window context
- image content in AI mode
- accepted past title patterns

## Title Acceptance

A title is accepted when one of these happens:

- user explicitly accepts it
- user clicks into it and leaves it unchanged
- user sees it twice and does not modify it
- user keeps using the same title across stable snapshots
- user enters a stronger title manually

## Silent Generation

Silent generation is allowed only after title or intent acceptance.

Allowed generated files after acceptance:

- relation reasoning
- project summary
- naming plan
- task brief
- downstream adapter files
- OpenClaw handoff prompt
- review sheet
- clipboard bundle

## Handoff Rule

ScenePack does not directly submit to OpenClaw in the current prototype.

It prepares a user-visible handoff package, then lets the user:

- preview the handoff content
- copy a compact text bundle
- drag generated files to another tool
- open the package directory for inspection

## Do Not Generate

ScenePack should not generate deeper files when:

- title confidence is low
- scene is highly mixed
- structure entropy is high
- the user has not accepted a title
- image content is needed but AI mode is disabled
- the system detects `should_not_infer`

## Product Behavior

Default state:

- save structural records
- show light title candidates
- avoid file noise

Accepted state:

- generate project-level files silently
- keep generation traceable
- allow user rollback or disable
