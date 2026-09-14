# 天然产物路线提取：续跑 10 篇（2026-09-10）

本批已完成 10 篇新增论文的候选结构转录、事实配置、标准格式导出和 SQLite 入库，共新增 **260 条文章内分子记录、183 个反应事件／操作组、71 条路线分支**。分子记录包括目标、中间体及参与构建骨架的底物；同一分子在不同文章中可分别出现。数据库去重分子数净增 223，不能把 260 当作新增独立化学物种数。

这些是**待独立化学审核的候选数据**。7 篇按可用正文的制备网络整理，3 篇仅有 SI；正文网络覆盖也不意味着全部历史前体、金属配合物和立体信息均已完整解决。Polycitorol 首步仍缺结构，Daphnepapytone 的配合物与副产物立体信息仍有明确缺口，因此不能宣称 10 篇均已得到完整化学真值。

## 逐篇结果

| 文章／目标（点击查看案例报告） | 分子 | 反应事件 | 路线分支 | 证据与边界 |
|---|---:|---:|---:|---|
| [Xanchryones A/B/I–N](../data/routes/paper-03987f5a75395436/report.html) | 55 | 40 | 28 | 正文＋SI；目标及区域异构体、模型反应、互变异构体。 |
| [Paliurine E](../data/routes/paper-f1d4d3ac12fade5a/report.html) | 15 | 12 | 4 | 仅 SI；分步和一锅法，Z/E 描述存在原文冲突。 |
| [Hyperprzewones A/B](../data/routes/paper-3d207c0789378667/report.html) | 22 | 15 | 8 | 正文含实验部分；衍生物及副反应分支，收率和试剂当量冲突。 |
| [Conidiogenone B](../data/routes/paper-7feec71cd6acc726/report.html) | 22 | 13 | 2 | 仅正文；两套路线，消旋体代表构型，混合酯中间体。 |
| [Bilaiaeacorenol B、Penicibilaenes A/B](../data/routes/paper-bff74b7b8a828b65/report.html) | 31 | 22 | 7 | 正文＋SI；片段制备、异构体回收及脱水副产物。 |
| [Platycaryanin A（含 Casuarictin 分支）](../data/routes/paper-03577c3c53263ea5/report.html) | 49 | 36 | 3 | 正文＋SI；参引前体作为边界，轴手性另存元数据。 |
| [Schibitubin G](../data/routes/paper-d7ad71a4c6e665ca/report.html) | 18 | 12 | 3 | 正文＋SI；双对映体与天然构型修订，未画出的对映系列操作合并记录。 |
| [Epoxy-hydroxyamoyphanes](../data/routes/paper-f01cc38f743d98f4/report.html) | 7 | 5 | 4 | 仅 SI；发酵来源作为起点，酸/碱分支及结晶衍生物。 |
| [Polycitorols A/B](../data/routes/paper-65486c490d434d36/report.html) | 9 | 8 | 4 | 仅 SI；首步底物 3/4 结构缺失，保留未解决事件，不能称完整全合成。 |
| [Daphnepapytone A](../data/routes/paper-e6385b951e04c2da/report.html) | 32 | 20 | 8 | 仅正文；R/S 起始系列、醛异构化、笼状副产物；配合物 26 和部分立体构型待补。 |
| **合计** | **260** | **183** | **71** | 候选数据，待独立审核 |

## 数据位置与使用

- [统一 SQLite](../data/atlas.sqlite)、[数据库总览](../data/database/report.html)
- [本批清单、逐篇 ID、计数和校验结果](../data/extraction/ten-paper-batch-20260910.json)
- [事实配置目录](../data/facts/)；每篇的 `data/facts/<paper_id>.json` 是可维护输入。
- 每篇 `data/routes/<paper_id>/` 下包含 `dataset.json`、`molecules.csv`、`reactions.csv`、`routes.json`、`molecules.sdf`、结构 SVG、HTML 报告及 SHA-256 校验清单。

分子表提供 RDKit **canonical isomeric SMILES**、原文编号、分子式、立体状态和证据页码。反应表分别保存底物／产物、试剂、溶剂、收率及其作用范围。路线表的 `molecule_smiles_sequence` 和 `step_reaction_smiles_sequence` 保存按依赖顺序排列的序列；多底物、汇合和分支应同时读取 `reactant_labels`、`product_labels` 和 `ordered_event_ids`，不能仅把分子列表当作单链路线。

反应 SMILES 是底物—产物表示，并未生成未经验证的原子映射。点分隔还可能表示原文混合物的多个组分；它不是自动推定的化学计量比。一锅多操作没有原文中间体图时，用 `operation_stages` 保留阶段，不能从总收率推造每个阶段的产物或分步收率。

## 尚未解决的事实

1. **Polycitorols A/B：** SI 首步报告醛 3 与膦酸酯 4 制备 5，但没有足够的起始结构图或名称。已解析网络从 5 开始，首步以 `unresolved_events` 保存；没有逆推补造 3/4 的 SMILES。
2. **Daphnepapytone A：** 26 为原文画出的钴配合物，金属—配体表示尚未验证；保留配体 25 和配合物形成／环化操作，并单列未解决记录。副产物 28 的连接关系已转录，新增中心 1/16/17（事实配置中的局部原子编号）暂不补猜立体标签。正文未画出的 S 系列早期中间体和炔丙醇混合物仅保留操作边界。
3. **Platycaryanin A：** HHDP 的轴向 S 指定保存在 `axial_stereochemistry`；普通四面体 isomeric SMILES 不完整编码阻转异构。苄叉缩醛中心及糖椅式仍需独立核对。参引的已知前体未补写本文不存在的上游实验。
4. **Amoyphane：** 中间体 3 的原文结构与所报含氧碳谱值需独立复核；目前保留图中结构并标为待审。
5. **消旋体、混合物与冲突：** Conidiogenone B、Acorane 系列使用明确限定的消旋体代表结构。Paliurine 的 Z/E 文字、Hyperprzewones 的收率／当量／温度、多个案例的 HRMS 或质量—物质的量存在来源冲突，已逐项保存。计算检查通过不消除原文矛盾。

这些限制应连同 SMILES 一起使用。全批 `formal_benchmark_eligible` 和 `admission_authority` 保持 false。

## 风险筛选与替换

沿用并更新 [detail-policy.json](../data/extraction/detail-policy.json)，全库当前 11 篇仅保留元数据。本批依据用户的保守排除要求新增排除：

- Caryopincaolide A：正文 p1 明确报告较强细胞毒性／诱导凋亡。
- Garvensintriol：正文 p6 将修订目标关联到已报道的强细胞毒性化合物。
- Kuhistanicaol G／Ferutinin：作者机构摘要强调较强抗癌活性；本地 SI 还存在字体和对象损坏。

这些文章未生成本批详细合成数据。替换原因、参考链接及来源边界已进入批次清单；另有仅含表征或缺失本地 PDF 的备选文章暂缓。筛选是本次数据处理范围决定，不是对其余全部目标、中间体或试剂的无风险认证。

## 校验与库内状态

源文件绑定保留页码和 SHA-256，原文、截图和复核拼图留在 `.local/`。转录后检查了 107 个关键分子的 SMILES 反向绘图；这属于本次转录复查，不是独立专家复核。

[案例审计](../data/extraction/case_audit.json)对全部 55 个案例通过了 schema、分子式、canonical SMILES、反应端点、路线拓扑、JSON／CSV 一致性、SDF 往返及文件校验。 [数据库审计](../data/extraction/database_validation.json)通过，检查 1,681 个去重分子及 14 项导出；RDKit 版本为 2026.03.6。本次没有修改编译器。

| 库内状态 | 本批前 | 本批后 |
|---|---:|---:|
| 候选提取论文 | 45 | 55 |
| 文章内分子记录 | 1,215 | 1,475 |
| 反应事件 | 797 | 980 |
| 路线分支 | 237 | 308 |
| 去重分子（含既有候选来源） | 1,458 | 1,681 |

全库 133 篇：55 篇候选已入库、53 篇待结构转录、14 篇缺少本地来源、11 篇仅保留元数据。已独立确认完整路线数仍为 0。

## 复现本批

在仓库根目录运行，复用现有事实配置及源文件缓存：

```powershell
$batch10 = Get-Content data/extraction/ten-paper-batch-20260910.json -Raw | ConvertFrom-Json
$batch10Args = @()
foreach ($paperId in $batch10.paper_ids) { $batch10Args += @('--paper', $paperId) }
.venv/Scripts/python.exe scripts/batch_extract_atlas.py @batch10Args
.venv/Scripts/python.exe scripts/audit_route_cases.py
.venv/Scripts/python.exe scripts/validate_atlas_database.py
```
