---
name: slbb-video-research-script
description: AI 短剧 S1 调研、剧情提取、剧情拆分、15 秒短视频分集拆解、人物关系整理和版权/改写风险提示。Use when the user provides a short drama name, platform, raw story, script, synopsis, Feishu/Markdown source material, or asks to perform “短剧调研”, “剧情提取”, “拆分剧情”, “生剧情提示词”, “版权筛查”, “改写成 AI 短视频剧情”, or prepare S1 artifacts for the slbb-video workflow.
---

# AI 短剧 S1：调研与剧情提取拆分

## Overview

Use this skill to turn a short-drama name, platform, raw plot, script, or research notes into S1 workflow artifacts for downstream image-prompt and video-prompt skills.

S1 must not call downstream S2/S3 work. It produces clean story structure and 15-second segments for S2. Research notes, rewrite/copyright risk notes, and confirmation notes belong in `_meta` or `_handoff`, not in the primary S1 outputs.

## Operating Gates

- 🔴 CHECKPOINT: before writing S1 primary outputs, classify the source as `researched`, `provided`, or `inferred`.
- 🔴 CHECKPOINT: before deciding the number of 15-second segments, complete a source coverage audit and write `artifacts/_meta/S1_segmentation_decision.md`.
- 🔴 CHECKPOINT: before marking S1 complete, every core character must have production-useful visual anchors for S2 three-view reference sheets.
- 🔴 CHECKPOINT: before entering S2, the user must confirm the story extraction and segmentation.
- 🛑 STOP: if the source material is too thin to identify core characters, core scene, and at least one episode, write a blocked handoff instead of inventing a full story.
- 🛑 STOP: if a full-season drama is being compressed but source coverage is too thin to justify a full-series segmentation, label the output as an inferred sample or block for more source material instead of choosing a fixed count.
- 🛑 STOP: if the work is based on copyrighted source material, keep long quotes/dialogue out of primary outputs and record rewrite risk in `_meta`.

## Workflow

1. Confirm the input type:
   - **V2 handoff (highest priority)**: if `workflow_state.json.source.v2_video_url` is non-empty, this run was imported via `bin/slbb-video-from-handoff`. Read the handoff as the primary source. `source.title` is the original benchmark video title; `source.matched_rules` lists the monitoring rules; `source.manual_note` carries operator context; `source.v2_metrics` is informational.
   - Drama name + platform: perform research if tools are available, and label unsupported details as inferred.
   - Raw story/script/synopsis: use the provided text as the primary source.
   - Existing S1 run directory: inspect existing artifacts before editing.
2. Audit source coverage before segmentation:
   - original total episode count, if known.
   - collected source count and material types: official synopsis, episode list, full transcript, platform clips, user-provided notes, or only search snippets.
   - verified plot coverage vs inferred/reconstructed coverage.
   - major narrative arcs and effective short-video hooks found in the material.
   - dynamic target segment count and why that number is appropriate for the available source.
3. Run `scripts/scaffold_s1_run.py` to create the S1 artifact skeleton when writing to files.
4. Read only the needed references:
   - `references/research_prompt.md` for the validated Feishu research prompt.
   - `references/decomposition_framework.md` for the standardized story decomposition template.
   - `references/output_contract.md` for required artifact filenames and validation rules.
5. Produce these required artifacts:
   - `artifacts/S1/story_extract.md`
   - `artifacts/S1/story_segments.json`
   - `artifacts/_meta/S1_segmentation_decision.md`
   - optional process notes under `artifacts/_meta/S1_research_notes.md` or `artifacts/_handoff/S1_human_confirmation_card.md`
6. Run `scripts/validate_s1_outputs.py <run_dir>` before claiming S1 is complete.
7. Stop at the human gate. Do not continue to S2 until the user confirms the story extraction and segmentation.

## Artifact Rules

- Write artifacts under the run directory, not inside the skill directory.
- Prefer a user-provided run directory. If none is provided, use the current working directory.
- Never hardcode a user-specific absolute path inside generated skill logic.
- Keep verified facts, inferred details, and invented rewrites clearly separated.
- Do not decide the compressed segment count by habit or template. Decide it from source coverage, original episode count, plot density, arc count, and usable 15-second hooks; record that decision in `_meta/S1_segmentation_decision.md`.
- Prepare S2 visual anchors in S1: every core character should have enough stable appearance detail for a one-image three-view character sheet, including face, hair, body shape, costume, shoes, accessories, and overall visual temperament when available.
- For known copyrighted works, do not reproduce long verbatim plot text or dialogue. Summarize, transform, and create original 15-second adaptations.
- Replace original role names in segment scripts with neutral names such as `小美`, `小刚`, `小秦`; keep original names only in the character research section.
- Primary outputs must be clean. Do not include workflow principles, version notes, risk analysis, or human-confirmation wording inside `story_extract.md` or `story_segments.json`.

## Minimum S1 Output

`story_extract.md` must include:

- One-sentence summary
- Core characters
- Core scenes
- Episode list
- Next-stage input for S2

The S2 input section must mention which characters need one-image three-view reference sheets and which scenes need empty-scene reference images.

`artifacts/_meta/S1_segmentation_decision.md` must include:

- source_type: `researched`, `provided`, or `inferred`.
- original_episode_count, if known.
- collected_source_count and material types.
- coverage_level: high / medium / low.
- target_segment_count: the exact number of 15-second units in `story_segments.json`.
- decision_basis: why this count fits the source coverage and story density.
- boundary: full-series reconstruction, compressed adaptation, sample-only inferred segmentation, or blocked.

`story_segments.json` must include a top-level `characters` array. Each character must include:

- `name`
- `role`
- `appearance`
- `relationship`
- `visual_anchor`

`visual_anchor` must include face, hair, body, costume, shoes, accessories, and temperament for S2 three-view character reference generation.

`story_segments.json` must include a top-level `episodes` array. Each episode must include:

- `episode_id`
- `episode_name`
- `scene`
- `characters`
- `props`
- `timeline`
- `review`

`timeline` must include three beats:

- `0-2s`
- `3-10s`
- `11-15s`

Each beat must contain camera language, physical action, and dialogue/sound. Do not leave dialogue/sound blank.

Human confirmation notes can be written to `artifacts/_handoff/S1_human_confirmation_card.md`, but that file is process support, not a primary S1 output.

## Failure Modes

| Trigger | Required action | Forbidden shortcut |
| --- | --- | --- |
| Drama name/platform research is unavailable | Label missing facts as `inferred` and ask for source material or user confirmation. | Do not present inferred plot as verified source. |
| Original episode count is known but source coverage is thin | Write a coverage audit, choose sample-only segmentation or block for more material. | Do not pick 8, 16, 20, or any other count just because it sounds reasonable. |
| User questions the compressed segment count | Return to S1, revise `S1_segmentation_decision.md`, and only then update `story_segments.json`. | Do not keep S2/S3 artifacts that depend on the old segmentation. |
| Raw story lacks character appearance | Fill only production-useful visual anchors and record inference notes in `_meta/S1_research_notes.md`. | Do not leave S2 without face, hair, body, costume, shoes, accessories, and temperament anchors. |
| Source is copyrighted or too close to an existing drama | Summarize, transform, rename roles, and keep risk notes out of primary outputs. | Do not copy long plot text or dialogue verbatim. |
| Episode segmentation cannot support 15 seconds | Mark the segment as blocked or split/merge with explanation in `_meta`. | Do not force three empty timeline beats. |
| `story_segments.json` fails validation | Fix the JSON shape before asking for human confirmation. | Do not continue to S2 with invalid JSON. |
| User asks to jump to image/video prompts | Finish S1 artifacts and human gate first. | Do not call S2/S3 from S1. |

## Anti-pattern Blacklist

- Do not hide whether details are verified, inferred, or invented for adaptation.
- Do not compress a long drama into a fixed number of 15-second units without a source coverage audit.
- Do not treat structural validation as proof that source coverage and segmentation count are correct.
- Do not put copyright analysis, source caveats, or human-gate prose in `story_extract.md` or `story_segments.json`.
- Do not leave any core character without visual anchors for S2.
- Do not keep original character names in segment scripts when an adapted neutral-name version is required.
- Do not produce S2 image prompts or S3 motion prompts inside S1.
- Do not mark S1 complete because the story sounds plausible; validation and user confirmation are required.
- Do not create empty `dialogue_or_sound` beats.

## Commands

Create the skeleton for a run:

```bash
python3 "$CODEX_SKILLS_ROOT/slbb-video-research-script/scripts/scaffold_s1_run.py" <run_dir>
```

If `CODEX_SKILLS_ROOT` is not set, replace it with the local skills root.

Validate outputs:

```bash
python3 "$CODEX_SKILLS_ROOT/slbb-video-research-script/scripts/validate_s1_outputs.py" <run_dir>
```

## Completion Gate

S1 is complete only when the two required clean artifacts exist, validation passes, and the user has confirmed the story gate. S1 approval is a human decision, not an automatic model decision.
