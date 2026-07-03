import subprocess
import sys
import tempfile
import unittest
import json
import struct
import zlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "acrylic-labubu-display-image"


SAMPLE_BRIEF = """product_name: "粉紫星星款潮玩亚克力展示盒"
product_type: "透明亚克力防尘展示盒"
product_size_cm:
  length: 18
  width: 14
  height: 22
inner_size_cm:
  length: 17.4
  width: 13.4
  height: 21.4
acrylic_thickness_mm: 3
box_structure: "单层，正面磁吸门，透明面板，彩绘边框"
target_figure_size: "适合 15-17cm 潮玩公仔"
new_release_theme: "粉紫星星，甜酷，梦幻收藏感"
color_palette:
  - "透明"
  - "粉紫"
  - "奶白"
  - "浅蓝点缀"
painting_style: "极简星星边框彩绘，角落小涂鸦，不遮挡透明展示"
main_selling_points:
  - "防尘保护"
  - "透明展示"
  - "加厚亚克力"
  - "磁吸开门"
  - "彩绘边框"
  - "桌搭收纳"
  - "适合收藏展示"
reference_images:
  - "/tmp/reference/new-release.png"
output_platform: "淘宝"
output_mode: "prompt_only"
image_ratio: "1:1"
"""

REFERENCE_ONLY_BRIEF = """product_name: "粉色毛绒娃适配亚克力展示盒"
reference_images:
  - "/tmp/reference/pink-fuzzy-doll.png"
output_platform: "淘宝"
output_mode: "prompt_only"
image_ratio: "1:1"
"""


def run_script(script_name, *args, check=True):
    script = SKILL_ROOT / "scripts" / script_name
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def make_png(width=100, height=100, color=(250, 250, 250)):
    raw_rows = []
    row = bytes(color) * width
    for _ in range(height):
        raw_rows.append(b"\x00" + row)
    payload = zlib.compress(b"".join(raw_rows))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", payload)
        + chunk(b"IEND", b"")
    )


class AcrylicSkillTests(unittest.TestCase):
    def test_skill_structure_and_project_docs_exist(self):
        required_files = [
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "agents" / "openai.yaml",
            SKILL_ROOT / "references" / "style-guide.md",
            SKILL_ROOT / "references" / "prompt-patterns.md",
            SKILL_ROOT / "references" / "figure-case-fit-rules.md",
            SKILL_ROOT / "references" / "painting-complexity-rules.md",
            SKILL_ROOT / "references" / "market-finished-poster-rules.md",
            SKILL_ROOT / "references" / "ecommerce-main-image-rules.md",
            SKILL_ROOT / "references" / "failure-cases.md",
            SKILL_ROOT / "references" / "ip-compliance-rules.md",
            SKILL_ROOT / "references" / "iteration-rules.md",
            SKILL_ROOT / "templates" / "product-brief.yaml",
            SKILL_ROOT / "templates" / "acrylic-painted-design-prompt.md",
            SKILL_ROOT / "templates" / "five-main-images-prompts.md",
            SKILL_ROOT / "templates" / "poster-overlay-plan.md",
            SKILL_ROOT / "templates" / "qa-report-template.md",
            SKILL_ROOT / "templates" / "iteration-log-template.md",
            SKILL_ROOT / "scripts" / "make_poster_overlay.py",
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "docs" / "PRD-acrylic-labubu-display-image.md",
            REPO_ROOT / "docs" / "SPEC-acrylic-labubu-display-image.md",
        ]
        missing = [str(path.relative_to(REPO_ROOT)) for path in required_files if not path.exists()]
        self.assertEqual([], missing)

        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: acrylic-labubu-display-image", skill_text)
        self.assertIn("默认只生成结构化提示词", skill_text)
        self.assertIn("只有用户明确要求", skill_text)
        self.assertIn("make_poster_overlay.py", skill_text)

        agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("亚克力盒生图", agents_text)
        self.assertIn("acrylic-labubu-display-image", agents_text)

    def test_build_prompts_creates_complete_prompt_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(SAMPLE_BRIEF, encoding="utf-8")

            result = run_script(
                "build_prompts.py",
                "--brief",
                brief_path,
                "--output-root",
                output_root,
                "--date",
                "2026-06-30",
            )

            self.assertIn("2026-06-30_", result.stdout)
            pack_dir = output_root / "2026-06-30_粉紫星星款潮玩亚克力展示盒"
            expected = [
                "creative_brief.yaml",
                "acrylic_painted_design_prompt.md",
                "main_image_01_white_background.md",
                "main_image_02_lifestyle_scene.md",
                "main_image_03_detail.md",
                "main_image_04_dimension_base.md",
                "main_image_05_selling_points.md",
                "poster_overlay_plan.md",
                "qa_report.md",
                "iteration_log.md",
            ]
            for name in expected:
                self.assertTrue((pack_dir / name).exists(), name)

            hero = (pack_dir / "main_image_01_white_background.md").read_text(encoding="utf-8")
            self.assertIn("【图片编号】", hero)
            self.assertIn("【英文生图提示词】", hero)
            self.assertIn("transparent acrylic display case", hero)
            self.assertIn("no text", hero)
            self.assertNotIn("official collaboration", hero.lower())

            dimension = (pack_dir / "main_image_04_dimension_base.md").read_text(encoding="utf-8")
            self.assertIn("尺寸文字和箭头后期叠加", dimension)
            self.assertIn("no text, no numbers", dimension)

    def test_market_finished_poster_mode_is_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(REFERENCE_ONLY_BRIEF, encoding="utf-8")

            run_script(
                "build_prompts.py",
                "--brief",
                brief_path,
                "--output-root",
                output_root,
                "--date",
                "2026-07-02",
            )

            pack_dir = output_root / "2026-07-02_粉色毛绒娃适配亚克力展示盒"
            brief = (pack_dir / "creative_brief.yaml").read_text(encoding="utf-8")
            self.assertIn('composition_mode: "market_finished_poster"', brief)
            self.assertIn('poster_layout: "left_text_right_product"', brief)
            self.assertIn('copy_overlay_policy: "post_production_only"', brief)
            self.assertIn('base_style: "black_display_base"', brief)
            self.assertIn('scene_style: "warm home collectible display"', brief)

            for name in ["main_image_02_lifestyle_scene.md", "main_image_05_selling_points.md"]:
                text = (pack_dir / name).read_text(encoding="utf-8")
                self.assertIn("market_finished_poster", text)
                self.assertIn("warm ecommerce poster composition", text)
                self.assertIn("product on the lower-right side", text)
                self.assertIn("large clean empty copy area on the upper-left", text)
                self.assertIn("left text area", text)
                self.assertIn("black display base", text)
                self.assertIn("warm home desktop scene", text)
                self.assertIn("post-production text overlay", text)
                self.assertIn("shallow depth of field", text)

            valid = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir)
            self.assertIn("PASS", valid.stdout)

    def test_text_is_post_production_overlay_not_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(REFERENCE_ONLY_BRIEF, encoding="utf-8")

            run_script("build_prompts.py", "--brief", brief_path, "--output-root", output_root, "--date", "2026-07-02")
            pack_dir = output_root / "2026-07-02_粉色毛绒娃适配亚克力展示盒"
            overlay = (pack_dir / "poster_overlay_plan.md").read_text(encoding="utf-8")

            self.assertIn("高清高透", overlay)
            self.assertIn("亚克力防尘罩", overlay)
            self.assertIn("桌面收藏更出片 · 潮流有新意", overlay)
            self.assertIn("post_production_only", overlay)
            self.assertIn("make_poster_overlay.py", overlay)
            self.assertIn("左上角", overlay)
            self.assertIn("主标题", overlay)
            self.assertIn("胶囊卖点", overlay)

            for path in pack_dir.glob("main_image_*.md"):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("generate Chinese title text", text)
                self.assertNotIn("render Chinese characters", text)
                self.assertIn("no text", text)
            self.assertIn("post-production text overlay", (pack_dir / "main_image_05_selling_points.md").read_text(encoding="utf-8"))

    def test_commercial_graphic_skin_complexity(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(REFERENCE_ONLY_BRIEF, encoding="utf-8")

            run_script("build_prompts.py", "--brief", brief_path, "--output-root", output_root, "--date", "2026-07-02")
            pack_dir = output_root / "2026-07-02_粉色毛绒娃适配亚克力展示盒"
            brief = (pack_dir / "creative_brief.yaml").read_text(encoding="utf-8")
            self.assertIn('painting_complexity: "commercial_graphic_skin"', brief)

            for name in [
                "acrylic_painted_design_prompt.md",
                "main_image_01_white_background.md",
                "main_image_02_lifestyle_scene.md",
                "main_image_05_selling_points.md",
            ]:
                text = (pack_dir / name).read_text(encoding="utf-8")
                self.assertIn("commercial graphic skin", text)
                self.assertIn("complete product-skin illustration", text)
                self.assertIn("large background shapes", text)
                self.assertIn("graffiti-like abstract lettering strokes", text)
                self.assertIn("side panel continuation", text)
                self.assertIn("layered stickers and torn-paper color blocks", text)
                self.assertIn("front panel hero graphic system", text)
                self.assertIn("not just a border", text)

            hero = pack_dir / "main_image_01_white_background.md"
            original_hero = hero.read_text(encoding="utf-8")
            hero.write_text(
                original_hero
                .replace("commercial graphic skin", "rich themed acrylic panel illustration")
                .replace("large background shapes", "small corner icons")
                .replace("graffiti-like abstract lettering strokes", "simple dots")
                .replace("side panel continuation", "plain side panel")
                .replace("not just a border", "simple border only"),
                encoding="utf-8",
            )
            invalid = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir, check=False)
            self.assertNotEqual(0, invalid.returncode)
            self.assertIn("commercial graphic skin", invalid.stdout.lower())

    def test_ultra_compact_fit_rules_are_injected_when_only_doll_reference_is_provided(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(REFERENCE_ONLY_BRIEF, encoding="utf-8")

            run_script(
                "build_prompts.py",
                "--brief",
                brief_path,
                "--output-root",
                output_root,
                "--date",
                "2026-06-30",
            )

            pack_dir = output_root / "2026-06-30_粉色毛绒娃适配亚克力展示盒"
            brief = (pack_dir / "creative_brief.yaml").read_text(encoding="utf-8")
            self.assertIn('fit_mode: "ultra_compact_fit"', brief)
            self.assertIn('figure_height_to_inner_height_ratio: "88%-92%"', brief)
            self.assertIn('figure_width_to_inner_width_ratio: "72%-82%"', brief)
            self.assertIn('top_clearance_ratio: "3%-7%"', brief)
            self.assertIn('side_clearance_ratio: "4%-8% each side"', brief)
            self.assertIn('bottom_clearance_ratio: "4%-8%"', brief)
            self.assertIn('depth_clearance_ratio: "6%-12% front/back"', brief)

            required_files = [
                "acrylic_painted_design_prompt.md",
                "main_image_01_white_background.md",
                "main_image_02_lifestyle_scene.md",
                "main_image_05_selling_points.md",
            ]
            for name in required_files:
                text = (pack_dir / name).read_text(encoding="utf-8")
                self.assertIn("ultra-compact custom-fit", text)
                self.assertIn("88%-92%", text)
                self.assertIn("72%-82%", text)
                self.assertIn("Shrink the acrylic case around the doll; do not shrink the doll to fit a large case.", text)
                self.assertIn("no tiny doll inside a big box", text)
                self.assertNotIn("The doll fills about 75% of the interior height.", text)
                self.assertNotIn("75%-78%", text)

            dimension = (pack_dir / "main_image_04_dimension_base.md").read_text(encoding="utf-8")
            self.assertIn("compact fitted proportion base image", dimension)
            self.assertIn("leave only realistic clearance around the doll silhouette", dimension)
            self.assertIn("no oversized case", dimension)
            self.assertIn("no text, no numbers", dimension)

            valid = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir)
            self.assertIn("PASS", valid.stdout)

    def test_no_magnetic_hardware_terms_in_positive_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(SAMPLE_BRIEF, encoding="utf-8")

            run_script(
                "build_prompts.py",
                "--brief",
                brief_path,
                "--output-root",
                output_root,
                "--date",
                "2026-06-30",
            )

            pack_dir = output_root / "2026-06-30_粉紫星星款潮玩亚克力展示盒"
            prohibited_positive_terms = [
                "magnetic front door",
                "magnetic door",
                "magnetic latch",
                "magnetic closure",
                "磁吸门",
                "磁吸点",
                "磁吸结构",
                "金属磁吸扣",
                "圆形磁吸点",
            ]
            prompt_files = [
                "acrylic_painted_design_prompt.md",
                "main_image_01_white_background.md",
                "main_image_02_lifestyle_scene.md",
                "main_image_03_detail.md",
                "main_image_04_dimension_base.md",
                "main_image_05_selling_points.md",
            ]
            for name in prompt_files:
                text = (pack_dir / name).read_text(encoding="utf-8")
                positive_text = text.split("【负面提示词】", 1)[0].lower()
                for term in prohibited_positive_terms:
                    self.assertNotIn(term.lower(), positive_text, f"{name} contains {term}")

            all_text = "\n".join((pack_dir / name).read_text(encoding="utf-8").lower() for name in prompt_files)
            self.assertIn("no magnetic door", all_text)
            self.assertIn("no round magnetic dots", all_text)
            self.assertIn("no visible magnets", all_text)

            valid = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir)
            self.assertIn("PASS", valid.stdout)

    def test_rich_theme_panel_painting_is_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(REFERENCE_ONLY_BRIEF, encoding="utf-8")

            run_script(
                "build_prompts.py",
                "--brief",
                brief_path,
                "--output-root",
                output_root,
                "--date",
                "2026-06-30",
            )

            pack_dir = output_root / "2026-06-30_粉色毛绒娃适配亚克力展示盒"
            brief = (pack_dir / "creative_brief.yaml").read_text(encoding="utf-8")
            self.assertIn('painting_complexity: "commercial_graphic_skin"', brief)
            self.assertIn('painting_coverage: "35%-55%"', brief)
            self.assertIn('painting_density: "medium-high"', brief)

            required_files = [
                "acrylic_painted_design_prompt.md",
                "main_image_01_white_background.md",
                "main_image_02_lifestyle_scene.md",
                "main_image_05_selling_points.md",
            ]
            for name in required_files:
                text = (pack_dir / name).read_text(encoding="utf-8")
                self.assertIn("rich themed acrylic panel illustration", text)
                self.assertIn("commercial graphic skin", text)
                self.assertIn("35%-55%", text)
                self.assertIn("medium-high density", text)
                self.assertIn("multi-layer hand-drawn decorative system", text)
                self.assertIn("not sparse corner-only stickers", text)
                self.assertNotIn("minimalist themed painted border", text)

            valid = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir)
            self.assertIn("PASS", valid.stdout)

    def test_validate_prompt_pack_accepts_generated_pack_and_rejects_official_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(SAMPLE_BRIEF, encoding="utf-8")
            run_script("build_prompts.py", "--brief", brief_path, "--output-root", output_root, "--date", "2026-06-30")
            pack_dir = output_root / "2026-06-30_粉紫星星款潮玩亚克力展示盒"

            valid = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir)
            self.assertIn("PASS", valid.stdout)

            hero_path = pack_dir / "main_image_01_white_background.md"
            original_hero = hero_path.read_text(encoding="utf-8")
            hero_path.write_text(
                original_hero + "\nThis is an official collaboration product.\n",
                encoding="utf-8",
            )
            invalid = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir, check=False)
            self.assertNotEqual(0, invalid.returncode)
            self.assertIn("official collaboration", invalid.stdout.lower())

            hero_path.write_text(
                original_hero + "\nUse large showcase cabinet proportions for the product.\n",
                encoding="utf-8",
            )
            oversized = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir, check=False)
            self.assertNotEqual(0, oversized.returncode)
            self.assertIn("large showcase cabinet", oversized.stdout.lower())

            hero_path.write_text(
                original_hero + "\nUse a generic showcase with an oversized display case as the product.\n",
                encoding="utf-8",
            )
            generic = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir, check=False)
            self.assertNotEqual(0, generic.returncode)
            self.assertIn("generic showcase", generic.stdout.lower())

    def test_validate_prompt_pack_rejects_missing_ultra_compact_fit_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(SAMPLE_BRIEF, encoding="utf-8")
            run_script("build_prompts.py", "--brief", brief_path, "--output-root", output_root, "--date", "2026-06-30")
            pack_dir = output_root / "2026-06-30_粉紫星星款潮玩亚克力展示盒"

            for path in pack_dir.glob("*.md"):
                text = path.read_text(encoding="utf-8")
                text = text.replace("ultra-compact", "compact")
                text = text.replace("ultra_compact_fit", "compact_fit")
                text = text.replace("88%-92%", "75%-78%")
                text = text.replace("72%-82%", "60%-65%")
                text = text.replace("3%-7%", "10%-18%")
                text = text.replace("Shrink the acrylic case around the doll; do not shrink the doll to fit a large case.", "")
                text = text.replace("no oversized acrylic display case", "no wrong scale")
                text = text.replace("no tiny doll inside a big box", "no wrong figure scale")
                text = text.replace("no large empty space above the doll", "no empty area")
                path.write_text(text, encoding="utf-8")

            invalid = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir, check=False)
            self.assertNotEqual(0, invalid.returncode)
            self.assertIn("ultra", invalid.stdout.lower())
            self.assertIn("88%", invalid.stdout.lower())
            self.assertIn("72%", invalid.stdout.lower())
            self.assertIn("75%", invalid.stdout.lower())
            self.assertIn("negative prompt", invalid.stdout.lower())

    def test_validate_prompt_pack_rejects_magnetic_terms_and_missing_rich_painting(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "product-brief.yaml"
            output_root = tmp_path / "outputs"
            brief_path.write_text(REFERENCE_ONLY_BRIEF, encoding="utf-8")
            run_script("build_prompts.py", "--brief", brief_path, "--output-root", output_root, "--date", "2026-06-30")
            pack_dir = output_root / "2026-06-30_粉色毛绒娃适配亚克力展示盒"

            hero_path = pack_dir / "main_image_01_white_background.md"
            original_hero = hero_path.read_text(encoding="utf-8")
            hero_path.write_text(
                original_hero.replace("【负面提示词】", "Use magnetic door hardware on the front panel.\n\n【负面提示词】"),
                encoding="utf-8",
            )
            magnetic = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir, check=False)
            self.assertNotEqual(0, magnetic.returncode)
            self.assertIn("magnetic", magnetic.stdout.lower())

            hero_path.write_text(original_hero, encoding="utf-8")
            for path in pack_dir.glob("*.md"):
                text = path.read_text(encoding="utf-8")
                text = text.replace("rich themed acrylic panel illustration", "simple painted border")
                text = text.replace("35%-55%", "5%-10%")
                text = text.replace("medium-high density", "low density")
                text = text.replace("multi-layer hand-drawn decorative system", "small corner stickers")
                text = text.replace("not sparse corner-only stickers", "sparse corner-only stickers")
                text = text.replace("no sparse tiny corner-only decorations", "no bad decorations")
                path.write_text(text, encoding="utf-8")
            sparse = run_script("validate_prompt_pack.py", "--pack-dir", pack_dir, check=False)
            self.assertNotEqual(0, sparse.returncode)
            self.assertIn("rich themed", sparse.stdout.lower())
            self.assertIn("35%-55%", sparse.stdout)

    def test_save_iteration_log_appends_feedback_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "iteration_log.md"
            run_script(
                "save_iteration_log.py",
                "--log",
                log_path,
                "--date",
                "2026-06-30",
                "--prompt-version",
                "v1",
                "--image-type",
                "01_white_background",
                "--image-path",
                "generated_images/01_white_background.png",
                "--user-feedback",
                "这张亚克力不透明，公仔太抢主体",
                "--issue-tags",
                "acrylic_not_clear,figure_too_dominant",
                "--accepted",
                "false",
                "--rejected-reason",
                "材质不透明且主体偏移",
                "--next-revision-instruction",
                "加强透明亚克力和产品主体占比",
                "--reusable-success-terms",
                "premium ecommerce product photography",
                "--banned-failure-terms",
                "glass cabinet",
            )
            text = log_path.read_text(encoding="utf-8")
            self.assertIn("2026-06-30", text)
            self.assertIn("figure_too_dominant", text)
            self.assertIn("加强透明亚克力", text)
            self.assertIn("glass cabinet", text)

    def test_make_dimension_overlay_writes_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.png"
            output = tmp_path / "dimension.png"
            source.write_bytes(make_png())
            run_script(
                "make_dimension_overlay.py",
                "--input",
                source,
                "--output",
                output,
                "--length",
                "18",
                "--width",
                "14",
                "--height",
                "22",
                "--inner-length",
                "17.4",
                "--inner-width",
                "13.4",
                "--inner-height",
                "21.4",
                "--fit-height",
                "17",
            )
            data = output.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertGreater(len(data), 100)

    def test_make_poster_overlay_writes_final_poster_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.png"
            overlay_plan = tmp_path / "poster_overlay_plan.md"
            output = tmp_path / "05_selling_points_final.png"
            debug_layout = tmp_path / "layout.json"
            source.write_bytes(make_png(width=900, height=1200, color=(245, 232, 214)))
            overlay_plan.write_text(
                """# Poster Overlay Plan

copy_overlay_policy: post_production_only
composition_mode: market_finished_poster
poster_layout: left_text_right_product

## 后期叠加文案

- 主标题：高清高透
- 副标题：亚克力防尘罩
- 胶囊卖点：桌面收藏更出片 · 潮流有新意
""",
                encoding="utf-8",
            )

            run_script(
                "make_poster_overlay.py",
                "--input",
                source,
                "--overlay-plan",
                overlay_plan,
                "--output",
                output,
                "--debug-layout",
                debug_layout,
            )

            data = output.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertGreater(len(data), len(source.read_bytes()))
            self.assertEqual((900, 1200), self.png_size(output))
            layout = json.loads(debug_layout.read_text(encoding="utf-8"))
            capsule = layout["capsuleRect"]
            text = layout["capsuleTextRect"]
            self.assertGreaterEqual(text["x"], capsule["x"] + capsule["paddingX"])
            self.assertGreaterEqual(text["y"], capsule["y"] + capsule["paddingY"])
            self.assertLessEqual(text["x"] + text["width"], capsule["x"] + capsule["width"] - capsule["paddingX"])
            self.assertLessEqual(text["y"] + text["height"], capsule["y"] + capsule["height"] - capsule["paddingY"])

    def png_size(self, path):
        data = Path(path).read_bytes()
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        return struct.unpack(">II", data[16:24])


if __name__ == "__main__":
    unittest.main()
