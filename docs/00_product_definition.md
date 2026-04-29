# Product Definition / 产品定义

Version: v0.1  
Product name: ScenePack

## One Sentence

ScenePack saves a user's desktop visual working scene as a high-quality structural context package, then lets AI or downstream tools continue from that structure.

中文：

ScenePack 保存的不是几张图片，而是用户整理思路时形成的视觉现场，并把这个现场转成后续 AI、文档、表格、项目工具可以继续使用的上下文。

## Core Pain

Users often collect many discrete materials:

- screenshots
- web pages
- tables
- prompts
- UI states
- product references
- design references
- error messages
- mixed project materials

They arrange these materials visually to think. Current tools preserve images, but usually lose the structure behind the arrangement.

The real pain:

> Discrete information is hard to turn into a usable aggregate state without manual explanation.

中文：

用户已经通过贴图、摆放、缩放、分区、留白、靠近、拉远等动作做了第一轮整理，但下游 AI 或工具通常接不住这层整理结果。

## What ScenePack Is

ScenePack is a visual aggregation layer.

It captures:

- layout facts
- structural relations
- cognitive practice signals
- candidate project titles
- scene stability
- generation readiness
- user confirmation state
- downstream handoff context

It does not initially claim to fully understand image content.

The current product shape is a compact tray workbench: capture first, inspect the scene visually, confirm the title, then hand clean context to downstream tools such as OpenClaw.

## Core Flow

The minimum product route is:

- `Silent Capture`: the bypass monitor observes the desktop and records stable scenes without interrupting the user.
- `Needs Confirmation`: ScenePack shows the captured structure, candidate titles, key references, risk, and image-reading need.
- `Ready To Handoff`: after the user confirms or rewrites the title, ScenePack generates a handoff package.
- `Handed Off`: the user copies or drags the package into OpenClaw or another downstream tool, and the package remains traceable.

This flow is the product spine. New features should either improve one of these states or make the transitions clearer.

## What ScenePack Is Not

ScenePack is not:

- a screenshot replacement
- a Snipaste clone
- a pure image manager
- a full knowledge base
- a default AI image analysis tool
- a project management system

It can integrate with these tools later, but the core product is the aggregation layer between visual work and downstream work.

## Product Principle

Structure can be light, but it cannot be rough.

中文：

结构可以轻，但不能粗糙。轻的是默认暴露量，不是底层结构质量。

## Default Behavior

The default system should:

- record first
- infer carefully
- generate later
- expose little
- preserve rich structure internally
- make confirmation explicit before deeper generation
- keep downstream handoff files easy to copy or drag out

The first default output is a scene record, not a project analysis result.
