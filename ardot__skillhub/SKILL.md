---
name: ardot-showcase-autolayout
version: 1.0.12
agent_created: true
description: 用于在 Ardot 中把多个已有画板自动编排成可交付的衍生展示区。适合多状态对照、设计评审看板、流程演示、角色/设备矩阵。也可作为 CodeBuddy + Ardot AI 设计工作流的收尾节点，将 AI 生成的零散画板自动整理成结构化展示区并输出可分享链接。
---

# 衍生展示区自动编排

## 极速上手

**前提**：已连接 Ardot MCP（`mcp__ardot-design__*` 命名空间），并在 Ardot 打开目标文件、选中要排版的画板。

**直接这样说**：
- 「把选中的画板用 ardot-showcase-autolayout 重新排版」
- 「顺便用这个技能把刚生成的画板规范化排版」
- 「把这几个画板排成评审展示区，发我链接」

**技能会做**：自动分组 → 选布局轴向 → 生成标题栏 + 分组 + 单元格小标题 → 找空位放置（绝不覆盖已有画板）→ 截图预览 → 返回 Ardot 链接。

**随时调整**：「白底 / 灰底 / 演示模式」「竖排 / 矩阵」「按设备分组」「日期写 X」。
> 内置 4 套主题：暗色评审 / 亮色评审 / 灰度护眼 / 演示汇报，用上面自然语言一键切换。

## 适用与边界

适合：多状态页面对照、设计评审看板、流程演示、角色 / 设备矩阵，以及 AI 设计工作流的收尾整理。
不处理：生成画板内部 UI、导出 PDF/PNG、跨多个 Ardot 文件编排、判断业务方案好坏。

## 典型场景

**多状态页面对照**（分组明确，可跳过确认）
触发：「把登录流程 5 屏（默认 / 输入 / 校验失败 / 加载 / 成功）排成 review board，链接发产品」
产出：单 group「状态对照」，ROW 横排 5 cell，同一链路不加分隔线。

**设计评审看板**（场景模糊，先确认分组）
触发：「把这个链接里的画布排版一下」（6 屏、命名重复）
产出：先给 2–4 个分组方案让你选（含「保持原样」「自定义」），再生成。

**多端组件矩阵**（MATRIX）
触发：「4 个按钮变体 × mobile / desktop 排成对照展示区」
产出：group = mobile / desktop 两行，MATRIX 排版。

**跨模块带分隔线**（divider 正式用法）
触发：「文件管理（列表 / 详情）+ 分享管理（创建链接 / 权限）排一起，模块间用分隔线」
产出：模块之间插 1 条 `RECTANGLE + height:"fill_container"` 分隔线，自动撑满行高；同一模块内部不加线。

## 四步工作流

1. **确定输入 + 目标页面**：优先用当前 Ardot selection；其次 agent 上一步刚生成的 nodeId；或你显式给的 nodeId / page。读不到时只问一次。
2. **场景理解与分组**：先定「谁和谁一组」再定「怎么排」；无法可靠推断时，给 2–4 个分组选项（含「保持原样」「自定义」）。分组方法见 `references/scene-grouping.md`。
3. **判断布局轴向**：看原始排布意图 + 尺寸阈值 + 语义评分，选 ROW / COLUMN / MATRIX；不靠内容类型拍脑袋，不生成超长横排。评分规则见 `references/layout-decision-tree.md`。
4. **生成骨架并放置**：走质量门禁 → 算 outer 尺寸 → `locate_available_space`（padding ≥ 400，禁手写坐标）→ `batch_edit` 生成 → `batch_read` 校验 → `capture_screenshot` 预览 → 返回链接。
   > Ardot 工具调用须带 `mcp__ardot-design__` 前缀（如 `mcp__ardot-design__batch_edit`）；旧版 `edits[]` 已弃用。生成前须读 `assets/preset-config.json` 拿实际主题数值。
   > 细节规范按需读：`references/skeleton-spec.md`（骨架数值 / 对齐 / divider）、`references/quality-harness.md`（质量门禁）、`references/presets.md`（主题）、`references/naming-conventions.md`（命名 / 文案规范）、`references/ardot-api-cheatsheet.md`（API 速查）、`references/dependencies.md`（环境排查）、`references/faq.md`、`references/examples.md`。

## 关键门禁（交付前必过）

1. 分组已确认（或满足跳过条件），没打散原结构。
2. 用了 `locate_available_space`，没覆盖 / 贴边已有画板。
3. 布局轴向过了原始排布 + 尺寸阈值 + 语义评分，没生成超长横排。
4. Titlebar / subtitle / group / cell row 左边缘对齐，主题对比度可读。
5. 命名、日期、subtitle、mini-title、outer 100px 圆角符合规范。
6. 若用 column divider：必须为 `RECTANGLE + height:"fill_container"`，且 `batch_read` 校验其 `absoluteBoundingBox.height` ≥ 相邻 cell 最大高度 95%（杜绝「只显示上半段」）。

出错不抛原始 API 报错，翻译成「发生了什么 + 你该做什么」。
