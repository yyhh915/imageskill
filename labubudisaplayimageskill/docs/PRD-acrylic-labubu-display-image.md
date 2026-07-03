# 亚克力展示盒商品图 Skill PRD

## Summary

创建 `acrylic-labubu-display-image` Codex Skill，用于把亚克力展示盒的尺寸、结构、彩绘主题、新品风格和参考图，稳定转成一套可复用的电商商品图提示词包。

第四阶段目标：默认从“单张好看的产品渲染图”升级到“竞品级电商主图海报底图”。场景图和卖点图应形成左上文案空间、右下产品、暖光家居桌面、黑色展示底座、浅景深背景的成品构图；中文标题和卖点只进入后期叠加方案，不交给生图模型直接生成。

第五阶段目标：补齐最终海报闭环。使用 `make_poster_overlay.py` 把无字海报底图和 `poster_overlay_plan.md` 合成为带中文标题、副标题、胶囊卖点的淘宝主图海报成品。

## Goals

- 默认只生成结构化提示词、QA 和迭代日志。
- 用户明确要求直接生图时，才进入 image2/GPT Image 出图流程。
- 固定输出 1 张亚克力彩绘设计图提示词和 5 张电商主图提示词。
- 默认输出 `poster_overlay_plan.md`，用于后期叠加中文标题、副标题和胶囊卖点。
- 提供 `make_poster_overlay.py`，把无字底图合成为 `final_images/05_selling_points_final.png`。
- 支持分组参考图：娃娃参考图、亚克力结构参考图、彩绘参考图、场景参考图分别进入不同提示词用途。
- 保持商品主体为亚克力展示盒、防尘盒或展柜。
- 默认使用 `market_finished_poster` 构图和 `commercial_graphic_skin` 彩绘复杂度。
- 避免误导为 Pop Mart、Labubu 官方商品、官方联名或玩偶随盒赠送。
- 把常见失败反馈转成稳定修复规则，减少重复调提示词成本。

## Users And Use Cases

- 电商运营：快速生成淘宝/详情页主图提示词。
- 商品图设计协作者：根据新品主题批量探索彩绘方向。
- Codex 使用者：在后续会话中复用同一套提示词工程流程。

## Functional Requirements

- 接收商品名、商品类型、外尺寸、内尺寸、厚度、结构、适配公仔尺寸、主题、配色、彩绘风格、卖点、参考图、平台、输出模式、图片比例。
- 参考图应支持 `doll_reference_images`、`acrylic_structure_reference_images`、`painting_reference_images`、`scene_reference_images` 四类分组；旧版 `reference_images` 继续兼容，默认按娃娃展示参考处理。
- 自动补全合理默认值，并在 `assumed_fields` 中标记。
- 生成 `creative_brief.yaml`。
- 生成 `acrylic_painted_design_prompt.md`。
- 生成 5 张主图提示词：白底主图、场景图、细节图、尺寸底图、卖点氛围图。
- 图 2 和图 5 默认采用竞品级海报构图：左上留文案、产品在中下/右下、暖光家居桌面场景、黑色展示底座、浅景深。
- 彩绘默认升级为完整商业图案皮肤：大面积背景图形、正面主题主视觉、侧面延展、抽象涂鸦字母笔触、多层贴纸和撕纸色块。
- 中文主标题、副标题、卖点文案只写入 `poster_overlay_plan.md`，不要求生图模型生成文字。
- 生图后运行 `make_poster_overlay.py`，将中文标题和卖点真实压到最终 PNG。
- 生成 `qa_report.md` 和 `iteration_log.md`。
- 提供校验脚本，检查字段完整性、IP 合规、尺寸文字控制、公仔主体风险、海报构图、后期文字叠加策略和彩绘复杂度。
- 提供尺寸图后期叠加脚本，不让生图模型直接画准确文字或箭头。

## Acceptance Criteria

- 示例 brief 可成功生成完整 prompt pack。
- 多参考图 brief 能保留四类参考图字段，并在提示词中明确每类图的用途。
- 校验脚本对生成结果返回 PASS。
- 校验脚本能拒绝官方联名、官方授权等误导语句。
- 尺寸图提示词明确要求 no text/no numbers，并预留后期叠加空间。
- 生成包默认包含 `composition_mode: "market_finished_poster"` 和 `poster_overlay_plan.md`。
- 图 2 和图 5 包含左上文案留白、右下产品构图、暖光家居桌面场景、黑色展示底座和后期文字叠加说明。
- 生图提示词不得要求模型直接生成中文标题、卖点或可读文字。
- `make_poster_overlay.py` 可用测试 PNG 生成尺寸一致、非空的最终 PNG。
- 彩绘提示词包含 `commercial graphic skin`、完整商品皮肤、正面主题图形、侧面延展和多层贴纸/色块。
- 迭代日志能记录反馈、问题标签、成功词和失败词。
