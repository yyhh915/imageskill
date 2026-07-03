# 亚克力展示盒商品图 Skill Spec

## Structure

```text
.agents/skills/acrylic-labubu-display-image/
  SKILL.md
  agents/openai.yaml
  references/
  templates/
  scripts/
  assets/
AGENTS.md
docs/
```

## Scripts

- `scripts/build_prompts.py`
  - Input: `--brief <yaml>`, `--output-root <dir>`, optional `--date YYYY-MM-DD`.
  - Output: one dated product folder containing creative brief, design prompt, five main-image prompts, poster overlay plan, QA report, and iteration log.
  - Dependencies: Python standard library only.

- `scripts/validate_prompt_pack.py`
  - Input: `--pack-dir <dir>`.
  - Checks required files, required fields, English prompt presence, negative prompt presence, QA presence, official-claim risk, dimension-text risk, and figure-subject risk.
  - Returns non-zero on validation failure.

- `scripts/save_iteration_log.py`
  - Appends structured markdown feedback entries to `iteration_log.md`.
  - Tracks prompt version, image type, image path, feedback, issue tags, acceptance, rejected reason, next revision instruction, reusable success terms, and banned failure terms.

- `scripts/make_dimension_overlay.py`
  - Input: clean base PNG and dimension values.
  - Output: PNG with simple dimension guide lines and labels.
  - Uses standard-library PNG writing so it runs without Pillow.

- `scripts/make_poster_overlay.py`
  - Input: no-text poster base PNG, `poster_overlay_plan.md`, and output path.
  - Output: final poster PNG with Chinese title, subtitle, and capsule selling-point overlay.
  - Uses macOS Swift/AppKit text rendering so Chinese copy is rendered by post-production code, not by the image model.
  - Returns a clear error if Swift is unavailable.

## 比例控制模块

- Rule file: `.agents/skills/acrylic-labubu-display-image/references/figure-case-fit-rules.md`.
- Default mode: `fit_mode: "ultra_compact_fit"`.
- Default use case: when the user only provides a doll reference image and no product dimensions, treat the figure as a 15-17cm collectible and generate an ultra-compact custom-fit acrylic dust cover, not a generic showcase or large cabinet.
- Default ratios:
  - `figure_height_to_inner_height_ratio: "88%-92%"`.
  - `figure_width_to_inner_width_ratio: "72%-82%"`.
  - `top_clearance_ratio: "3%-7%"`.
  - `side_clearance_ratio: "4%-8% each side"`.
  - `bottom_clearance_ratio: "4%-8%"`.
  - `depth_clearance_ratio: "6%-12% front/back"`.
- Required English controls:
  - `The acrylic display case is an ultra-compact custom-fit dust cover for this doll, not a generic showcase.`
  - `The doll fills 88%-92% of the interior height.`
  - `The doll fills 72%-82% of the interior width.`
  - `Leave only 3%-7% top clearance above the doll.`
  - `Leave only narrow side clearance around the ears and arms.`
  - `Keep the case depth shallow and fitted, not a deep cube.`
  - `Shrink the acrylic case around the doll; do not shrink the doll to fit a large case.`
  - `Do not make the acrylic case larger to show it as the product; show the product through clear edges, seams, clean acrylic front panel, and rich painted panel art.`
- Injection scope: strong injection in `acrylic_painted_design_prompt.md`, `main_image_01_white_background.md`, `main_image_02_lifestyle_scene.md`, and `main_image_05_selling_points.md`; light fit reminder in `main_image_03_detail.md`; compact fitted case reminder in `main_image_04_dimension_base.md` while preserving the clean base image and post-production dimension overlay workflow.
- Negative prompt library must include: `no oversized acrylic display case`, `no giant acrylic box`, `no generic large showcase`, `no large empty space above the doll`, `no excessive side clearance`, `no excessive depth inside the case`, `no tiny doll inside a big box`, `no cube-like oversized display cabinet`, `no display case much taller than the doll`, `no wide empty interior around the figure`, and `no product made oversized to dominate the doll`.

## 第二阶段比例修复：ultra_compact_fit

The first compact-fit pass used a 75% interior-height target. Test images still looked like oversized generic cabinets: too much top clearance, side clearance, and depth, with the doll visually small inside the box. The second-stage fix makes `ultra_compact_fit` the default for reference-image-only briefs.

Subject rule correction:

- Wrong interpretation: "the acrylic case is the subject" means the case should be much larger than the doll.
- Correct interpretation: the acrylic case is the subject through material, structure, transparent edges, clean front panel, seams, and rich painted panel art.
- The interior must stay close to the doll's real fitted size.
- The product image should communicate "the case just protects and displays the doll", not "a doll standing in a huge empty cabinet".

Validation behavior:

- `validate_prompt_pack.py` fails packs missing `ultra-compact` or `ultra_compact_fit`.
- It fails packs missing 88%-92% height fit, 72%-82% width fit, 3%-7% top clearance, or shrink-the-case-not-the-doll wording.
- It fails packs whose negative prompt lacks `no oversized acrylic display case`, `no tiny doll inside a big box`, or `no large empty space above the doll`.
- It fails packs that still use the old 75% default fit wording.
- It rejects positive uses of `large showcase cabinet`, `generic showcase`, or `oversized display case`.

## 第三阶段结构和彩绘复杂度修复

Latest image tests showed two new failure modes after the fit ratio was fixed: the model kept adding round magnetic hardware, and the painting looked like sparse corner decorations instead of a themed acrylic product skin.

Structure correction:

- This product defaults to no magnetic hardware.
- Default `box_structure`: `单层，透明亚克力防尘罩，透明面板，彩绘边框和主题面板，干净透明正面开合面板`.
- Positive prompts must not generate magnetic doors, round magnetic dots, metal magnetic buttons, visible magnets, magnetic latches, or magnetic closure hardware.
- The case should use a clean acrylic front panel, transparent front opening panel, sliding acrylic panel, lift-off acrylic cover, or seamless clear acrylic cover language.
- Negative prompts must include `no magnetic door`, `no round magnetic dots`, and `no visible magnets`.

Painting complexity correction:

- Third-stage baseline introduced `rich_theme_panel`; fourth-stage default is now `commercial_graphic_skin` while retaining rich theme controls for density and anti-sparse validation.
- Default `painting_coverage`: `35%-55%`.
- Default `painting_density`: `medium-high`.
- The front panel should include a rich themed illustration while the center doll-viewing area stays transparent.
- The side panel continues the same theme at lower density.
- The painting system can include large themed background shapes, decorative borders, stickers, doodles, stars, flowers, ribbons, abstract lettering strokes, and partial translucent overlays.
- It must not copy readable brand text, official lettering, logos, or IP-specific marks.

Validation behavior:

- `validate_prompt_pack.py` fails if positive prompt sections contain `magnetic`, `磁吸`, `round magnet`, `圆形磁吸点`, or `金属磁吸扣`.
- It fails if negative prompts omit `no magnetic door`, `no round magnetic dots`, or `no visible magnets`.
- It fails if the prompt pack omits `rich themed acrylic panel illustration`, `35%-55%`, `medium-high density`, `multi-layer hand-drawn decorative system`, or sparse-decoration prevention.
- It fails if the pack falls back to `minimalist themed painted border` without rich theme panel controls.

## 第四阶段竞品级电商成品图模式

Default poster mode:

- `composition_mode: "market_finished_poster"`.
- `poster_layout: "left_text_right_product"`.
- `copy_overlay_policy: "post_production_only"`.
- `base_style: "black_display_base"`.
- `scene_style: "warm home collectible display"`.

Composition behavior:

- The goal is a finished ecommerce poster base, not a centered product render.
- Images 2 and 5 use a left-text/right-product layout.
- Product sits in the lower-right or lower-middle area and occupies about 40%-55% of the image.
- The upper-left area stays clean for later title and selling-point overlay.
- Scene uses warm home desktop staging: soft window light, table lamp glow, books, vase, curtain, shelf depth, and shallow depth of field.
- A black or dark gray display base is added by default for a more finished commercial display feel.

Copy overlay behavior:

- `build_prompts.py` writes `poster_overlay_plan.md`.
- Default post-production copy:
  - 主标题：高清高透
  - 副标题：亚克力防尘罩
  - 胶囊卖点：桌面收藏更出片 · 潮流有新意
- Main-image prompts reserve the left text area but do not ask the image model to render Chinese text.
- Dimensions, arrows, labels, titles, price, and selling-point copy remain post-production only.

Commercial graphic skin behavior:

- Default `painting_complexity`: `commercial_graphic_skin`.
- The acrylic graphics must feel like a complete product-skin illustration, not just a border.
- Required controls include `commercial graphic skin`, `complete product-skin illustration`, `large background shapes`, `graffiti-like abstract lettering strokes`, `side panel continuation`, `layered stickers and torn-paper color blocks`, `front panel hero graphic system`, and `not just a border`.
- The central viewing area remains transparent so the figure is visible.
- The prompt must not copy competitor text, logos, brands, official packaging, or IP-specific marks.

Validation behavior:

- `validate_prompt_pack.py` requires `poster_overlay_plan.md`.
- It fails if images 2 or 5 omit `market_finished_poster`, `left text area`, `black display base`, `post-production text overlay`, `warm home desktop scene`, or shallow depth-of-field poster wording.
- It fails if the prompt asks the image model to generate Chinese title text or render Chinese characters in the positive prompt section.
- It fails if design prompt, image 1, image 2, or image 5 omit commercial graphic skin complexity markers.

## 第五阶段最终海报合成

The fourth-stage prompt pack intentionally generates no-text poster base images. The final ecommerce-poster feel comes from post-production typography.

Workflow:

- Generate `generated_images/05_selling_points.png` from `main_image_05_selling_points.md`.
- Run `scripts/make_poster_overlay.py`.
- Use `poster_overlay_plan.md` for copy and layout.
- Write `final_images/05_selling_points_final.png`.

Default command:

```bash
python3 .agents/skills/acrylic-labubu-display-image/scripts/make_poster_overlay.py \
  --input generated_images/05_selling_points.png \
  --overlay-plan outputs/yyyy-mm-dd_product-name/poster_overlay_plan.md \
  --output final_images/05_selling_points_final.png
```

Rendering behavior:

- Main title: `高清高透`.
- Subtitle: `亚克力防尘罩`.
- Capsule selling point: `桌面收藏更出片 · 潮流有新意`.
- Default placement is the reserved upper-left copy area.
- Default styling uses warm brown title text and a light translucent capsule background.
- Text must not cover the acrylic case or doll display area.

Validation behavior:

- `validate_prompt_pack.py` requires `poster_overlay_plan.md` to mention `make_poster_overlay.py`.
- Unit tests run `make_poster_overlay.py` against a generated test PNG and require a valid same-size output PNG.

## Output Files

```text
outputs/yyyy-mm-dd_product-name/
  creative_brief.yaml
  acrylic_painted_design_prompt.md
  main_image_01_white_background.md
  main_image_02_lifestyle_scene.md
  main_image_03_detail.md
  main_image_04_dimension_base.md
  main_image_05_selling_points.md
  poster_overlay_plan.md
  qa_report.md
  iteration_log.md
```

## Compliance Rules

- Never present the product as an official Pop Mart/Labubu item.
- Never imply the figure is bundled with the acrylic case.
- Avoid generated logos, packaging marks, exact brand text, prices, labels, dimensions, or large text.
- Keep Chinese title and selling-point copy in `poster_overlay_plan.md` for post-production overlay only.
- Use copy such as "仅售亚克力展示盒，图中公仔仅作场景展示" when buyer clarity is needed.

## Verification

Run:

```bash
python3 -m unittest discover -s tests -v
python3 .agents/skills/acrylic-labubu-display-image/scripts/build_prompts.py --brief .agents/skills/acrylic-labubu-display-image/templates/product-brief.yaml --output-root outputs --date 2026-06-30
python3 .agents/skills/acrylic-labubu-display-image/scripts/validate_prompt_pack.py --pack-dir outputs/2026-06-30_粉紫星星款潮玩亚克力展示盒
python3 /Users/Admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/acrylic-labubu-display-image
```

## Acceptance Criteria

- A brief with only doll reference images and no size fields outputs `fit_mode: "ultra_compact_fit"` in `creative_brief.yaml`.
- The design prompt and main images 1, 2, and 5 explicitly state that the doll fills 88%-92% of the interior height and 72%-82% of the interior width.
- The prompt pack explicitly says: `Shrink the acrylic case around the doll; do not shrink the doll to fit a large case.`
- Negative prompts reject oversized acrylic display cases, tiny dolls inside big boxes, and large empty space above the doll.
- `validate_prompt_pack.py` fails prompt packs that omit ultra-compact wording, omit the 88%-92% / 72%-82% fit rules, omit shrink-the-case-not-the-doll wording, omit scale-control negative prompts, keep the old 75% default ratio, or positively instruct large/generic showcase proportions.
- New generated prompts contain no magnetic hardware terms in positive prompt sections.
- Negative prompts explicitly reject magnetic doors, round magnetic dots, and visible magnets.
- Default generated prompts use `commercial_graphic_skin` while retaining rich themed panel controls: 35%-55% decorative coverage, medium-high density, a multi-layer hand-drawn decorative system, a richer front panel, side-panel continuation, and a transparent central viewing area.
- `validate_prompt_pack.py` fails prompt packs that reintroduce magnetic hardware or under-designed sparse corner-only painting.
- A reference-image-only brief outputs `composition_mode: "market_finished_poster"`, `poster_layout: "left_text_right_product"`, `copy_overlay_policy: "post_production_only"`, and `base_style: "black_display_base"`.
- Generated packs include `poster_overlay_plan.md` with default Chinese title, subtitle, and capsule selling-point copy for post-production overlay.
- Images 2 and 5 reserve a left text area, place product lower-right/lower-middle, use a warm home desktop scene, include a black display base, and avoid generated Chinese text.
- Default generated prompts use `commercial_graphic_skin` with complete product-skin illustration, large background shapes, front panel hero graphic system, side panel continuation, graffiti-like abstract lettering strokes, and layered stickers/torn-paper color blocks.
- `make_poster_overlay.py` can turn a no-text poster base PNG into a final same-size PNG with real Chinese title, subtitle, and capsule selling-point overlay.
