# 独立证据包与事实配置：两篇提取实测

本轮完成两篇此前没有案例路线数据的文章，已统一进入 [SQLite 数据库](../data/atlas.sqlite)。分子使用 canonical isomeric SMILES，仍为来源绑定、待独立化学复核的候选提取。

| 文章 | 分子记录 | 制备事件 | 路线 | 来源 HRMS 检查 |
|---|---:|---:|---:|---:|
| [Acaulone B](../data/routes/paper-4cc43638c809d619/report.html) | 7 | 5 | 4 | 3 |
| [Triplinone F / 11-epi-Triplinone F](../data/routes/paper-6f84dc000b1334a0/report.html) | 46 | 40 | 5 | 30 |
| 合计 | 53 | 45 | 9 | 33 |

Acaulone B 从本篇画出的已知大环底物 4 开始，不外推引用文献的上游合成；副产物 9 的新立体中心未被擅自补全。Triplinone F 包括 SI 中的苹果酸起始步骤、双片段汇聚、回收异构体的构型翻转、两条 C11 构型路线和用于表征的缩醛支线。控制化合物 9a/9b 的新苄叉缩醛中心仍待核对，明确保留为未指定。

## 1. 每篇独立的证据包

`scripts/fact_case.py packet` 为一个 `paper_id` 生成一个私有证据窗口，路径为 `.local/evidence-packages/<paper_id>/active.json`。窗口仅包含该篇标题、一个来源及其 SHA、请求的有限页原文、已确认事实和待解问题。程序不把其他文章的内容或全库数据放入窗口。

- 默认反馈只有页码、字符数、重复页标记和私有文件路径；显式 `--show` 才输出所需原文。
- 原文窗口默认上限为 12,000 字符；超限返回错误，要求缩小页码范围。
- 页面内容哈希去重，默认不重复输出已经读过且未变化的页；复核使用 `--repeat`。
- 修改压缩规则后重用本地原始页文本，缓存图片存在时不重新打开 PDF。
- 完整论文、完整光谱和原始长日志留在私有目录。本次没有下载新的来源。
- `data/facts/sources/` 保存由程序锁定的来源指纹。来源字节、文章身份或来源清单改变时，事实编译会停止，避免把旧结论静默绑定到新来源。

这实现了**新增检索内容的逐篇隔离**。本轮仍在原来的长会话中运行，已有会话历史仍进入模型上下文和缓存输入统计；证据包本身不会清空历史。真正衡量独立短上下文的效果，需要在分别启动的新模型会话中复现实验。本轮不宣称已经进行了这种会话隔离测试。

## 2. 模型写事实，程序生成完整数据

本轮唯一需要人工/模型整理的化学输入是：

- [Acaulone B 事实配置](../data/facts/paper-4cc43638c809d619.json)
- [Triplinone F 事实配置](../data/facts/paper-6f84dc000b1334a0.json)

配置记录分子连接、原图楔线或明确 R/S、来源页码、反应两端、收率口径、条件、目标路径以及未解决问题。重复结构片段和立体化学图形模板可以复用。模板只展开显式记录的连接事实，不推断反应产物。

通用程序 `scripts/fact_case.py` 自动完成：

1. 检查文章身份和固定来源哈希。
2. 展开事实模板；必要时由缓存的本地 OPSIN 解析来源系统命名。
3. 根据原图坐标和实/虚楔线生成四面体构型；**先去掉临时原子编号，再核对 CIP R/S**，防止编号参与 RDKit 排序。
4. canonical SMILES、分子式、HRMS、模式及路线拓扑检查。
5. 生成完整 JSON、CSV、SDF、SVG 和 HTML。
6. 批处理自动发现 `data/facts/paper-*.json`，不需要新增逐篇适配器代码或手工维护注册表。
7. 无变化时跳过案例；集中入库一次，数据库无变化时跳过重建。

常规反馈只返回计数、缓存状态、来源冲突标识和错误。生成的完整配置与过程日志保存在 `.local/`，完整数据保存到 `data/routes/`，无需作为模型输入重复返回。

## 检查结果

[本轮验证记录](../data/extraction/isolated-two-paper-validation-20260909.json)保存了案例数量、生成文件体积、数据库检查和缓存复跑结果。

- 新流程及相关回归检查 18 项通过；后续涉及批处理和计量的 18 项检查也通过，两组测试有重叠，不相加当作独立测试数。
- 33 条来源 HRMS 分子式核对通过；来源数值精度和未指定立体化学仍需独立复核。
- 全库 39 篇 [案例审计](../data/extraction/case_audit.json)通过，37 篇沿用原审计缓存。
- SQLite 完整性及外键检查通过；累计 1,120 条文章内分子记录、727 个事件、840 个操作组、209 条路线。
- 两篇复跑均为 `unchanged`，数据库也为 `unchanged`。

## Token 记录及解释

[实测 token JSON](../data/extraction/isolated-two-papers-20260909-token-usage.json)读取本轮本地 `token_usage_record` 数字记录，按响应 ID 去重，只统计选定 turn；不导出消息、思考内容或其他会话数据。此次使用独立 run ID，没有覆盖之前的两篇实验记录。

记录分为共享选择/计量设置、Acaulone 证据和事实、Triplinone 证据和事实、共享验证/入库/报告四个阶段。阶段按实际记录时间归类，跨工具边界会有少量归属偏差，不能视为两个隔离模型调用的精确成本。

- `input_tokens`：包括缓存命中的输入。
- `cached_input_tokens`：输入的子集，不能重复相加。
- `uncached_input_tokens`：输入减缓存输入。
- `output_tokens`：输出；`reasoning_output_tokens` 是其子集，不能重复相加。
- `total_tokens`：输入加输出，不是账单价格。

计量从本轮第一条 usage 记录开始，包括工作流改造、来源核验、事实整理、程序修正、验证和回复，而非只统计论文阅读。后台监听器在本轮结束、最后的 usage 记录稳定后自动把 `measurement_finalized` 标记为 true，因此能补入最终回复的用量。结束前给出的数字均为当时快照，不冒充最终总量。

本轮长会话缓存输入仍然占显著比例；不能仅凭审阅文件变小就宣称整轮 token 按相同比例降低，也不能将两篇合计除二后的数字视作所有文章的普遍成本。

## 调用示例

```powershell
# 按需加载同一篇的有限证据，不显示全文时只返回摘要
.venv/Scripts/python.exe scripts/fact_case.py packet --paper paper-4cc43638c809d619 --source si --pages 3 4 --show

# 首次来源锁定；已有绑定不会自动替换
.venv/Scripts/python.exe scripts/fact_case.py bind --paper paper-4cc43638c809d619

# 编辑该篇事实 JSON 后，由程序生成所有输出
.venv/Scripts/python.exe scripts/fact_case.py build --paper paper-4cc43638c809d619

# 两篇集中增量入库
.venv/Scripts/python.exe scripts/batch_extract_atlas.py --paper paper-4cc43638c809d619 --paper paper-6f84dc000b1334a0

# 本轮计量快照，保留此前实验文件
.venv/Scripts/python.exe scripts/measure_extraction_tokens.py snapshot --run-id isolated-two-papers-20260909
```
