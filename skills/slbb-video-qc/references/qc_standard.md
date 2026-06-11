# S5 QC Standard

Source: whiteboard S5 nodes and project plan. The linked `质检表格` is a Feishu sheet, but current access could not read its contents on 2026-05-23. This first version uses the available whiteboard requirements.

## Review Methods

Record the method used:

- `human`: user or operator manually watched the video
- `frames`: extracted frames or screenshots were reviewed
- `gemini`: Gemini or another video-capable model reviewed the video
- `vision_model`: another model reviewed frames/video
- `notes_only`: user supplied issue notes without video access

Do not hide the review method. If no video/frame evidence is available, mark confidence low.

## Categories

| Category | What To Check | Likely Upstream Source |
| --- | --- | --- |
| character_consistency | face drift, body drift, clothing drift, random new person | S2 / platform |
| deformation | face/body/hand distortion, broken anatomy, unnatural eyes or mouth | S2 / S3 / platform |
| action_correctness | action does not match prompt, wrong sequence, missing key action | S3 / platform |
| expression_emotion | expression does not match conflict or dialogue | S1 / S3 / platform |
| lighting_color | too dark, inconsistent lighting, wrong atmosphere | S2 / S3 / platform |
| camera_stability | shaky, zoom weirdness, framing issue, subject lost | S3 / platform |
| scene_prop_consistency | wrong scene, missing prop, prop changes, background conflict | S2 / S3 / platform |
| dialogue_lipsync_story | dialogue mismatch, lip-sync mismatch, story meaning changed | S1 / S3 / platform |
| subtitle_text_glitch | garbled text, unwanted subtitles, watermark-like text | S3 / platform / S6 |
| platform_artifact | generation noise, flicker, morphing, impossible motion | platform / S4 |
| compliance_safety | unsafe visual expression or risky scene | S1 / S3 |
| long_drama_continuity | same-person identity drift across age stages, implausible age transition, broken emotional continuity between adjacent long-drama segments | S1_long_replica / S2 / S3 / platform |

## Severity

- `critical`: cannot publish or continue; must rework.
- `high`: harms story or viewer trust; should rework before edit.
- `medium`: visible issue; can choose rework or edit depending on cost.
- `low`: minor polish issue; can continue.

## Verdict

- `pass`: can continue to S6.
- `needs_rework`: route back to S2, S3, or S4.
- `reject`: cannot use this generated version.
- `blocked_no_video`: no video/frame evidence, cannot QC.

## Attribution Heuristics

- If character face/clothes are unstable from the first frame, likely S2 or platform.
- If first frame is right but motion goes wrong, likely S3 or platform.
- If action order is wrong, likely S3 shot table.
- If scene or props are wrong, check S2 scene reference and S3 scene lock.
- If subtitles are garbled but picture is usable, route to S6 editing fix.
- If problem appears in only one generation version, likely S4 platform attempt/platform randomness.
- If all versions have the same conceptual issue, route upstream to S1/S2/S3.
