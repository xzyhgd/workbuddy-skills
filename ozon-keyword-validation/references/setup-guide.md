# 环境配置与恢复指南

本 Skill 有两种安全工作方式：

1. **离线证据分析**：用户提供 SKU 导出、页面截图或原始数据；不需要 API 或浏览器自动读取。
2. **只读页面/接口辅助读取**：用户在自己的浏览器登录官方页面，或由受信任宿主用外部安全存储中的只读凭据读取 SKU 标题；Skill 不保存凭据。

先运行：

```text
python scripts/check_environment.py
```

需要同时检查脱敏授权状态或项目目录时，由可信宿主写入不包含任何秘密值的 probe JSON，再传入 `--probe-results`；环境检查本身不联网、不登录、不安装、不启动 daemon、不修改文件。

依赖标识：`python-runtime`、`ozon-seller-readonly`、`human-browser-session`、`project-evidence-directory`。以下各节与依赖清单逐项对应。

## `python-runtime`

- 用途：运行只读环境检查器与本地结构化检查。
- 支持版本：Python 3.10 或更高。
- 官方主页：https://www.python.org/
- 官方文档：https://docs.python.org/3/using/windows.html
- 下载地址：https://www.python.org/downloads/
- 配置：安装后执行 `python --version`，再执行 `python scripts/check_environment.py`。
- 验证：仅读取 Python 版本，不访问网络。
- 失效处理：版本过低时从官方来源升级后重检。
- 凭据、轮换、撤销：不适用。
- 核验日期：2026-11-20。

## `ozon-seller-readonly`：Ozon Seller 只读 SKU 读取

- 用途：读取本店 `offer_id`、俄语标题和用于属性词提炼的参数。
- 官方主页/登录：https://seller.ozon.ru/
- 官方文档：https://docs.ozon.ru/global/
- 官方入口：Seller Portal → Settings → API keys；实际菜单以当前官方界面为准。
- 所需权限：只需满足读取本店商品标题和参数的最小权限；不申请商品编辑、价格、库存、广告或推广权限。
- 凭据存储：仅放在用户控制的 Secret 管理器、受信任宿主或 Ozon 官方系统中；不得粘贴到对话或任何 Skill 文件。
- 白名单请求：仅 `POST /v3/product/list` 与 `POST /v3/product/info/list`，域名只能为 `api-seller.ozon.ru`。
- 验证：由受信任宿主执行最小只读探测，只返回 `ready`、`missing`、`unavailable` 或 `unknown` 的脱敏状态。
- 失效、权限或额度：在 Ozon 官方后台重新授权、轮换或由账户管理员处理；无法恢复时改用用户导出的标题和参数。
- 轮换和撤销：在官方 API Key 管理入口轮换或删除不需要的 Key；页面名称以当前官方界面为准。
- 核验日期：2026-11-20。

## `human-browser-session`：人工浏览器（Ozon 与 Wordstat）

- 用途：读取 Ozon 搜索查询页面、PDP、Wordstat 频次和 Dynamics 趋势。
- Ozon 登录：https://seller.ozon.ru/
- 站内搜索查询报表：国内站 `https://seller.ozonru.cn/app/analytics/what-to-sell/all-queries`，国际站 `https://seller.ozon.ru/app/analytics/what-to-sell/all-queries`；`/app/analytics/search-queries` 不是该报表，主区域空白时不要在其中抄数。
- Wordstat 页面：https://wordstat.yandex.ru/
- 操作：在用户自己的浏览器完成登录；页面中确认关键词、日期范围、筛选、地区和设备可见后再读取。
- 最小权限：只读查看、搜索、切换指标、导出和截图；不更改任何后台设置。
- 凭据存储：密码、Cookie、会话与 Token 只留在用户浏览器或官方系统中。
- 验证：目标页面可见，且能够在证据中看到读数和上下文。
- 窗口口径：页面只显示相对窗口且绝对日期不可见时，停下让用户选择严格 `UNVERIFIED` / 接受相对窗口加抓取日 / 用户补绝对日期；决定写入 manifest，不得自行接受相对窗口。
- 人机验证：出现 Qrator、Captcha、滑块、307→403 时停止自动化操作，由用户手动处理；不得换代理、破解验证、关闭 TLS 或改扩展设置。
- 失效处理：登录失效时在官方页面重新登录；页面不可用时改由用户提供原始截图或导出。
- 轮换与撤销：在各官方账户的安全/会话管理页面退出不需要的会话；页面名称以当前界面为准。
- 核验日期：2026-11-20。

## `project-evidence-directory`：项目证据目录

- 用途：保存 `ozon-keyword-pipeline/` 内的 CSV、截图、manifest、进度和阻断记录。
- WorkBuddy 官方说明：https://www.workbuddy.cn/docs/workbuddy/Overview
- 配置：选择用户确认的项目内目录；不使用个人目录、系统目录或未授权路径。
- 验证：环境检查只确认目录存在且可写，不创建、覆盖或删除文件。
- 不可用时：仅输出目录与字段清单，标“部分验证”；不能称本地证据已完成。
- 凭据、轮换、撤销：不适用。
- 核验日期：2026-11-20。

## Wordstat API 升级路径

本版本默认走网页人工可见读取，不申请 Wordstat API。需要批量化时，先在 Yandex Cloud/AI Studio 的官方 Search API 文档中确认当前产品开通、IAM 角色、配额、地区和 REST/gRPC 方法，再新建升级设计；不可从网页凭据、Cookie 或未核验第三方示例迁移。升级后也必须保留频次与趋势的实际查询式、窗口、地区、设备与原始证据。

## 功能级降级

| 功能 | 失败条件 | 降级方式 | 限制 | 恢复方式 | 停止条件 |
|---|---|---|---|---|---|
| SKU 标题读取 | API 未配置或不可用 | 用户导出/截图 | 不宣称 API 已验证 | 恢复安全授权后重检 | 无标题和参数时不能提种子词 |
| Ozon 搜索查询 | 未登录、验证、页面错误或字段变化 | 用户截图/导出 | 无窗口或字段映射时为 UNVERIFIED | 人工浏览器恢复后重采集 | 无 Ozon 证据不能做站内判断 |
| 绝对窗口日期不可见 | 非 Premium 只显示“时期: 7 天” | 停下让用户选择窗口口径 | 未拍板前全部相关行 `UNVERIFIED` | 用户确认相对窗口或补绝对日期后重判 | 不得自行用相对窗口或编造日期 |
| Wordstat | 登录、稳定性或验证问题 | 用户频次/趋势截图 | 缺一源不能判绿黄红 | 恢复页面后每词每源最多三次 | 无 Wordstat 证据不能做交叉判断 |
| 证据落盘 | 目录无权限或未授权 | 输出待保存清单 | 不称本地审计包完成 | 提供项目目录后保存 | 要求审计包但无任何存储位置 |
