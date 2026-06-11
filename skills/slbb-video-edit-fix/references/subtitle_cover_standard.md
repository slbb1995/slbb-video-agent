# S6 Subtitle Cover Standard

Source: whiteboard S6 nodes.

## Primary Use Case

AI-generated video sometimes adds unstable or garbled subtitles. The first S6 fix is to cover those subtitles.

## Default Style

- Background: white rectangle or white rounded rectangle if the editor tool makes it easier
- Text: black
- Font: commercially usable bold sans-serif
- Preferred font family: 黑体, 思源黑体, Noto Sans CJK, or equivalent
- Text position: placed over or near the original subtitle area, with the original text fully hidden
- Opacity: 100% for the cover block unless the user explicitly chooses another style
- Safety margin: cover block should exceed original bad text bounding box by at least 8-16 px

## Do

- Hide every frame where garbled text appears.
- Keep subtitle meaning consistent with S3 original dialogue.
- Keep contrast high enough for mobile viewing.
- Avoid covering important faces, hands, props, or story actions.
- Use one stable subtitle style across the whole clip.

## Do Not

- Do not use decorative fonts.
- Do not use copyrighted or unlicensed fonts.
- Do not leave the original garbled text partially visible.
- Do not rewrite story meaning while replacing subtitles.
- Do not claim editing is done without an edited output file or user confirmation.

## Human Editor Notes

For 剪映/CapCut-style editing, the typical manual process is:

1. Import selected video.
2. Locate the bad subtitle/text timestamps.
3. Add a white mask/block over the original text area.
4. Add black text above the mask using a commercially usable bold sans-serif font.
5. Preview frame by frame at each timestamp.
6. Export test version.
7. Recheck that no original garbled text leaks through.
