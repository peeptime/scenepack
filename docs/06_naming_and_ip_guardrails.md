# Naming And IP Guardrails / 命名与商业风险边界

Version: v0.1

## Public Name

Recommended public product name:

- ScenePack

Legacy engineering codename:

- Peepaste

Public materials should use `ScenePack`. Internal compatibility paths may still use `peepaste` for now.

## Naming Risk

The older name `Peepaste` created two avoidable problems:

- AI translation drift produced misleading output
- the sound and structure were too close to Snipaste

Public naming should therefore move away from `paste`-shaped branding.

Recommendation:

- use `ScenePack` as the default public name
- keep `peepaste` only where engineering compatibility still requires it
- do not use Snipaste in the product name
- use "works with Snipaste" only in descriptive text when necessary
- do not use Snipaste logo, UI branding, or visual identity

## Chinese And Japanese Names

Chinese and Japanese names are not decided yet.

Naming direction should avoid direct dependency on "paste" or "Snipaste".

Candidate meaning directions:

- visual scene
- context package
- material aggregation
- desktop scene
- structured capture
- thinking board

Avoid names that imply:

- official Snipaste extension
- replacement for Snipaste
- reverse engineered Snipaste
- guaranteed AI understanding

## Snipaste Boundary

ScenePack should not:

- modify Snipaste
- decompile Snipaste
- reverse engineer Snipaste
- bypass Snipaste licensing
- claim official partnership without permission

ScenePack may:

- observe desktop windows through normal OS APIs
- capture user-owned screen state with consent
- save references to user-created screenshots
- describe compatibility as "works with Snipaste" if true and necessary

## License Notes

Public Snipaste information states that Snipaste 2.x is free for personal non-commercial use, and business use requires a Pro license. The EULA also restricts modifying, reverse engineering, decompiling, or disassembling the software.

Sources checked:

- https://www.snipaste.com/
- https://www.snipaste.com/eula.html
- https://www.snipaste.com/licenses.html

These notes are product guardrails, not legal advice.

## Microsoft And Windows Naming

Microsoft guidance for Windows apps generally warns against implying official certification, endorsement, or license without formal agreement.

Use plain descriptive language:

- "for Windows"
- "works with Windows"
- "designed for Windows desktop workflows"

Avoid:

- "official Windows"
- "certified by Microsoft"
- Microsoft logos without permission

Reference:

- https://learn.microsoft.com/en-us/windows/apps/publish/partner-center/trademark-and-copyright-protection

## Patent Guardrails

Before commercial launch, ScenePack should run a professional patent and trademark review.

Engineering mitigation:

- document original structure pool design
- avoid copying proprietary UI behavior
- use public APIs
- keep implementation independent
- keep dated design records
- separate generic algorithms from product-specific claims

## Public Positioning

Recommended public positioning:

> A desktop visual aggregation tool that turns scattered working materials into structured project context.

中文：

> 一个把桌面离散材料整理成结构化项目上下文的视觉聚合工具。

Avoid:

> An AI Snipaste replacement.

Avoid:

> Official Snipaste AI extension.

