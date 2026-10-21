---
name: lanhu-to-liquid
description: 通过 Lanhu MCP 将蓝湖（Lanhu）设计稿自动转换为 Shopify Online Store 2.0 Liquid 主题代码（sections/snippets + schema + assets/CSS），含像素级自检、token 映射与防硬编码规则。当用户说"按蓝湖设计稿改/生成 Shopify 主题 section"、"把这张蓝湖图还原成 Liquid"、"蓝湖转 Shopify"时使用。
---

# 蓝湖 → Shopify Liquid 主题 自动化转换 SOP

让 AI 直接读取蓝湖设计稿，生成符合 Online Store 2.0 规范的 Liquid 代码，并对现有主题做像素级还原。

## 前置条件

- Lanhu MCP Server 已在运行，地址 `http://localhost:8000/mcp`（由 WorkBuddy `mcp.json` 的 `lanhu` 条目连接）。
- `.env` 已配置 `LANHU_COOKIE`（蓝湖网页版登录后的 Cookie）。
- 目标项目是 OS 2.0 主题结构：`layout/ sections/ snippets/ templates/ assets/ config/`。若当前工作区没有这些目录，先向用户确认主题根目录路径。
- 使用支持**视觉**的模型（Claude / GPT-4o / Gemini / Qwen / DeepSeek 等）。

## 可用 Lanhu MCP 工具

- `lanhu_get_designs` —— 获取 UI 设计图列表（必先于分析调用）
- `lanhu_get_ai_analyze_design_result` —— 分析某张设计图，返回**精确视觉参数**（尺寸/间距/颜色/字体/行高）及转换后的 **HTML+CSS 参考代码**
- `lanhu_get_design_slices` —— 获取切图信息并下载图标/素材到本地
- `lanhu_resolve_invite_link` —— 解析分享链接
- `lanhu_get_pages` / `lanhu_get_ai_analyze_page_result` —— 原型/需求文档分析（非 UI 场景用）

## 工作流（严格按顺序，不可跳过）

**Step 1 · 定位设计稿**
用户提供蓝湖链接（含 `tid`/`pid`/`docId`）。先调用 `lanhu_get_designs` 拿到设计图列表，确认要还原的是哪一张。

**Step 2 · 隔离读取（subagent）**
调用 `lanhu_get_ai_analyze_design_result` 获取结构化参数。注意：蓝湖原始 HTML 数据量很大，用独立 subagent 读取，**只把"路径 + 元素摘要 + 视觉参数表"返回主流程**，避免冲淡主会话里项目文档（components.md / dev-spec.md）的上下文。

**Step 3 · 视觉参数提取表（CoT，必须显式输出）**
从分析结果中抽取并列出：主色/辅助色、字号阶梯、行高、外/内边距、圆角、字重、字体家族、图标尺寸。对照项目 `dev-spec.md` 的 **token 映射表**，把蓝湖原始值映射到项目既有 CSS 变量或 theme settings。

**Step 4 · 组件拆分计划**
先查 `sections/`、`snippets/`、`docs/components.md`：
- 能复用现有 snippet/section 的，优先复用，不重复造轮子；
- 需要新建的，规划文件名（snake_case）与挂载位置（哪个 `templates/*.json` 引用）。

**Step 5 · 生成代码**
- `sections/<name>.liquid`：结构 HTML + Liquid 数据对象（`{{ product.title }}`、`{% for %}`、`{% if %}`）+ `{% schema %}`（定义 `settings`/`blocks`，让商家后台可视化配置）。
- `snippets/<name>.liquid`：可复用小组件，用 `{% render 'name', ... %}` 调用。
- `assets/<name>.css`：样式用 **CSS 变量 / theme settings 引用**，**禁止把蓝湖颜色值/间距硬编码写死**。
- 切图：调用 `lanhu_get_design_slices` 下载，按 snake_case 命名存入 `assets/`，Liquid 中用 `{{ 'xxx.png' | asset_url }}` 引用；图片加 `loading="lazy"`。
- 如需新页面类型，写 `templates/<page>.json` 引用上面 section。

**Step 6 · 像素级自检清单（生成后必须逐项核对）**
- [ ] 行高 line-height 与蓝湖一致（防止垂直居中失效）
- [ ] 特殊字体（如数字用 DIN/等宽）已约束
- [ ] 固定底栏/吸底元素加了 `padding-bottom` 安全区，避免被遮挡
- [ ] 间距、圆角 1:1 使用蓝湖参数，未臆造
- [ ] 移动端断点正常（主题用 mobile-first）
- [ ] 对比度/可访问性（alt 文本、焦点态）达标
- [ ] 未引入 React/Vue 等重型框架（主题内只用原生 JS / AlpineJS）

**Step 7 · 交付与复盘**
- 标出所有 **TODO**：API 路径、枚举值、不确定的业务逻辑——**不猜测、不硬编码**。
- 输出一段简短复盘：还原了什么、复用了哪些组件、哪些值待用户确认。
- **防中断**：生成与自检连续执行，不要在"切图下载好了/代码生成好了"处停下来追问用户，一气呵成后再交付。

## 红线规则

1. **不硬编码 design token**：蓝湖给 `#7C3AED`、`16px` 必须映射到 `var(--color-primary)` / `var(--space-2)` 或 `settings_schema.json`，绝不直接写进 CSS/HTML。
2. **不臆造数值**：padding/line-height/间距严格来自 Step 3 参数表，缺参数就标 TODO。
3. **主题保持轻量**：禁止在主题内引入重型 JS 框架；交互用原生/AlpineJS。
4. **切图走 MCP**：用 `lanhu_get_design_slices` 下载并按规范命名，不手动另存。
5. **Cookie 安全**：`.env` 含蓝湖 Cookie，绝不提交 git；Cookie 过期需用户重新获取。

## 常见失败与对策

- 分析结果拿不到转代码：让设计师升级蓝湖插件版本后重新上传设计稿（开启"设计稿转代码"）。
- 截图空白：确认已执行 `playwright install chromium`。
- 还原度差：先在蓝湖开启"设计稿转代码"，MCP 的 HTML+CSS 参考会更准。
- 模型无视觉能力：换用支持视觉的模型，否则无法解析设计图。
