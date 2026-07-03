# labubudisaplayimageskill

Codex Skill for generating ecommerce image prompt packs for acrylic collectible-toy display cases, then composing final Taobao-style poster images with post-production Chinese text overlays.

## What It Does

- Builds a structured prompt pack from a doll/reference image brief.
- Keeps the product subject as the acrylic display case, not the toy.
- Defaults to compact doll-to-case proportions.
- Avoids generated Chinese text in image models.
- Generates a no-text poster base prompt and a `poster_overlay_plan.md`.
- Uses `make_poster_overlay.py` to render Chinese title, subtitle, and selling-point copy onto the final poster image.

## Main Skill Path

```text
.agents/skills/acrylic-labubu-display-image/
```

## Generate Prompt Pack

```bash
python3 .agents/skills/acrylic-labubu-display-image/scripts/build_prompts.py \
  --brief .agents/skills/acrylic-labubu-display-image/templates/product-brief.yaml \
  --output-root outputs
```

## Validate Prompt Pack

```bash
python3 .agents/skills/acrylic-labubu-display-image/scripts/validate_prompt_pack.py \
  --pack-dir outputs/yyyy-mm-dd_product-name
```

## Compose Final Poster Text

Generate a no-text poster base image first, then run:

```bash
python3 .agents/skills/acrylic-labubu-display-image/scripts/make_poster_overlay.py \
  --input generated_images/05_selling_points.png \
  --overlay-plan outputs/yyyy-mm-dd_product-name/poster_overlay_plan.md \
  --output final_images/05_selling_points_final.png
```

## Run Tests

```bash
python3 -m unittest discover -s tests -v
```

## Compliance

This Skill must not claim official Pop Mart/Labubu collaboration, authorization, accessories, packaging, logos, or bundled toys. Figures in generated images are display props only.
