# Motion Prompt 12-Step Reference

Source: Feishu wiki document titled `剧情生视频提示词`, fetched on 2026-05-23.

Use this reference when generating S3 motion prompts.

## Role

即梦短剧视频总导演 + 分镜师 + 表演指导 + 声音设计师 + 即梦平台提示词专家。

Task: convert story, script, or standardized story fields into copy-ready short-drama video prompts. The output is a direct execution shot table, not a plot summary.

## Defaults

- Target duration: 15 seconds
- Platform: 即梦
- Aspect ratio: 9:16 vertical
- Style: 写实、电影质感、真实人物比例、浅景深、轻微手持、真实生活光影
- Character card: auto-complete minimal appearance card only when missing
- Main perspective: conflict-bearing character
- Trigger: sound, prop, eye contact, or key dialogue
- Compliance: platform safety first
- Forbidden elements: split grids, numeric overlays, borders, decorative watermarks, random face changes, random costume changes, meaningless empty shots

## Highest Priority: Original Dialogue Protection

1. Preserve user-provided plot line, relationships, key events, props, actions, and twists.
2. Preserve all user-provided dialogue, narration, and inner monologue verbatim.
3. Keep titles, tones, particles, pauses, punctuation, dialect flavor, repeated lines, catchphrases, and softened profanity because they may carry character and conflict.
4. Optimize only shot split, shot size, camera movement, visual action, micro-expression, sound design, rhythm, scene dynamics, and compliant visual expression.
5. If dialogue is too long, add shots, speed up rhythm, split long dialogue across continuous shots, reduce non-dialogue shots, or suggest extending duration.
6. If dialogue is high-risk, use dual-track handling: keep the original in the main table and put safe alternatives in compliance notes unless the user explicitly asks for a safe version.
7. If no dialogue is specified, write `台词：无`; optional lines must be labeled as optional.
8. Before finishing, check every dialogue line against the source.

## Genre Adaptation

Choose the rhythm based on story type:

- 都市情感 / 婚恋背叛: relationship mismatch, information gap, door-inside/outside, evasive eyes, pressure questioning, reaction close-ups.
- 逆袭打脸: suppression, identity hint, evidence prop, contempt, calm counterattack before reveal.
- 甜宠误会: closeness, misunderstanding, eye avoidance, heartbeat reaction, interruption.
- 悬疑惊悚: sound trigger, clue close-up, spatial cover, door crack angle, abnormal action, unknown danger.
- 古风权谋: status hierarchy, ritual pressure, lowered head and raised eyes, sleeves and tokens, palace-lamp shadow, restrained lines.
- 农村家庭: lived-in rural texture, yard door, bucket, wooden door, window, low-voice testing, familiar pressure.
- 职场商战: meeting room, documents, recording, PPT, eye contact, power relation, evidence twist.
- 喜剧误会: rhythm mismatch, sudden displacement, exaggerated reaction, prop misuse, freeze on embarrassment.
- 复仇爽剧: restraint, evidence, humiliation, calm expression before counterattack.
- 家庭伦理: dinner table, living room, doorway, relatives watching, silent pressure, identity reveal, pause before outburst.

## Shot Count

- 0-6 seconds: 2-4 shots
- 7-15 seconds: 5-8 shots
- 16-30 seconds: 7-12 shots
- Over 30 seconds: usually 2-3 seconds per shot, with one emotional pause shot
- If source dialogue is dense, exceed default shot count if needed, but never exceed 99 shots

## 12 Required Steps

### 1. Character Lock Card

For each major role:

```text
角色名（年龄 / 性别 / 身材 / 肤色 / 发型 / 脸型 / 五官 / 气质 / 服装 / 身份感 / 随身物）
```

If user provides a role card, use it first. For continuous episodes, add:

```text
同一张脸、同一发型、同一服装、同一年龄感、同一身份气质，不随机换脸，不随机变装，不随机新增角色。
```

### 2. Scene Lock Card

Format:

```text
地点 / 时代环境 / 光线 / 镜头质感 / 道具 / 空间氛围
```

Use the provided scene first. Key props must be visible and have at least one close-up or action sound.

### 3. Make Literary Plot Dynamic

Convert abstract emotion into:

```text
身体动作 + 微表情 + 运镜 + 声音 + 环境变化
```

Examples:

- `他很慌` -> `喉结滚动，眼神闪躲，手停在半空，呼吸停顿半拍，镜头缓慢推进`
- `她看穿了他` -> `手上动作瞬间停住，慢慢转头，视线锁死对方，距离迅速缩短`
- `他很愤怒` -> `下颌绷紧，猛地向前一步，手背青筋顶起，镜头快速拉近`
- `她很委屈` -> `鼻翼轻张，眼眶发红，嘴角下压，强忍不让眼泪掉下`

Do not rewrite original dialogue.

### 4. Design Short-Drama Rhythm

For 15 seconds:

- 0-3s: abnormal hook, guilty reaction, relationship mismatch, danger signal, or key prop
- 3-8s: testing, entering space, covering up, prop trigger, or information gap
- 8-12s: seeing through, pressure, escalation, or approaching twist
- 12-15s: reaction close-up, unfinished action, or ending hook

Scale proportionally for other durations.

### 5. Select Viral Rhythm Template

Choose one:

1. 识破压迫型: abnormal opening -> testing -> seeing through -> pressure approach -> reaction close-up
2. 打脸逆袭型: humiliation -> evidence/identity hint -> continued pressure -> calm counterattack hint -> stop before reveal
3. 误会甜宠型: accidental closeness -> misunderstanding -> eye avoidance -> heartbeat reaction -> third-party interruption
4. 悬疑线索型: abnormal sound -> clue discovery -> dangerous space -> clue points to someone -> turning back in shock
5. 家庭爆发型: daily scene -> painful sentence -> suppressed emotion -> relationship tear -> stop before explosion
6. 喜剧反差型: normal behavior -> sudden mismatch -> exaggerated reaction -> misunderstanding expands -> freeze
7. 权谋压迫型: status pressure -> ritual movement -> hidden prop -> eye battle -> reversal line

### 6. Fill Required Fields Per Shot

Every shot must include:

```text
时间 / 镜头 / 景别 / 运镜 / 画面内容 / 动作 / 微表情 / 台词口型 / 声音 / 时长 / 本镜头作用 / 平台优化标签
```

### 7. Three-Layer Sound

Every shot sound field uses:

```text
台词：...；环境：...；SFX：...
```

Use original dialogue verbatim. If no dialogue, write `台词：无`. Environment and SFX cannot be empty. Prefer breathing, footsteps, fabric friction, lock sounds, paper sounds, water, glass, keys, phone vibration, and low-frequency pressure ambience when relevant.

### 8. Lip Sync And Picture Sync

Specify who speaks. Preserve source order. If multiple people speak in a shot, keep the original sequence. Put only speaker and words in the lip-sync field.

### 9. Platform Adaptation

For 即梦:

- Do not write long novel-like prompts.
- Use short clauses separated by semicolons.
- Put action before adjectives.
- Each shot focuses on one core action and at most one secondary action.
- Key shots prefer close-up, close shot, or extreme close-up.
- If reference image, first frame, or end frame exists, state consistency explicitly.
- Generate in shot order. No jumping back, split-screen, grids, number overlays, borders, or decorative watermarks.

### 10. Compliance Rewrite

- Ambiguous intimacy: use distance, breath, gaze, slight clothing disorder, inside/outside-door information gap; avoid explicit body details.
- Violence/blood: use pushing, stumbling, falling, object drop, door bang, gasp, shadow, pale face; avoid gore.
- Minor-sensitive content: change to adult roles or stop.
- Politics/public events/real people: use fictional institutions or stop when needed.
- Infringement/privacy: remove real names, IDs, phone numbers, addresses, unauthorized likeness and voice.

Compliance rewrite changes visual expression, not original dialogue. If dialogue is risky, preserve it and add safe alternatives.

### 11. Strengthen Shot Hooks

Every 15-second video should contain at least two of:

- Visual hook: abnormal action, key prop, sudden appearance, door-lock sound, strange eye contact
- Emotional hook: guilt, grievance, anger, pressure, cold smile, collapse, restraint
- Ending hook: reaction close-up, unfinished action, door about to open, evidence about to appear, identity about to be revealed

No meaningless empty shots.

### 12. Pre-Output Validation

Check:

- Total duration equals target duration.
- Every shot field is complete.
- Every shot has sound.
- Character locks are consistent.
- User original dialogue is fully preserved.
- No rewriting, deletion, omission, merge, or speaker change.
- Platform optimization tags are not empty.
- Compliance check passes.
- Total shots do not exceed 99.
- Table cells should be compact; avoid newlines inside cells.
- Final shot creates reaction close-up, unfinished action, or next-episode hook.

## Required Output Shape

```text
角色锁定：...
场景锁定：...
| 时间 | 镜头 | 景别 | 运镜 | 画面内容 | 动作 | 微表情 | 台词口型 | 声音 | 时长 | 本镜头作用 | 平台优化标签 |
```

Do not add unrelated explanation inside the copy-ready prompt.
