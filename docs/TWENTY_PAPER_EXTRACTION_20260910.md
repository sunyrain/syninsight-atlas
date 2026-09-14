# 天然产物路线提取：续跑 20 篇（2026-09-10）

本批新增 **20 篇候选提取案例、745 条文章内分子记录、624 个反应事件／操作组、175 条路线分支**，已导出并写入 SQLite。全库去重分子净增 **696**；文章内分子记录数不是独立化学物种数。

**这不等于 20 篇均已获得完整、经独立审核的化学真值。** 15 篇有正文路线证据（9 篇同时有 SI，6 篇仅正文），5 篇仅有 SI。Brevione 的部分模型／失败分支以及多篇的立体信息仍待补；引用前体的缺失步骤未逆推补造。全部数据保留候选状态，独立化学准入数量仍为 0。

## 逐篇结果

| 案例报告 | 分子记录 | 反应事件 | 路线分支 | 来源与边界 |
|---|---:|---:|---:|---|
| [Venezuelaene A](../data/routes/paper-fc94daed8713ef1e/report.html) | 36 | 29 | 4 | 正文＋SI；Nazarov／复分解路线及早期分支；未标明的醇与波浪键中心保留未指定。 |
| [Malbrancheamide B](../data/routes/paper-e8695c1d3895d8c6/report.html) | 15 | 13 | 4 | 仅正文；仿生环化、混合物及桥环副产物；23 的 SDF 立体信息已核对。 |
| [Voratin C](../data/routes/paper-8736f8c2a9e952ac/report.html) | 43 | 31 | 6 | 正文＋SI；环氧开环／螺缩酮；C17 名称与图示冲突待复核。 |
| [Isoplagiochin D](../data/routes/paper-960f0a43f7299433/report.html) | 14 | 10 | 1 | 正文＋SI；轴手性 M 与 ee 另存，普通四面体 SMILES 不完整表达轴手性。 |
| [Macrocephadiolide A](../data/routes/paper-fd21dcae86bb47e8/report.html) | 13 | 11 | 8 | 仅正文；氧化重排及分支；9／10 部分立体未指定，FeCl2／FeCl3 标注冲突。 |
| [Eudesmane 系列](../data/routes/paper-002ed49144be1357/report.html) | 42 | 29 | 17 | 正文＋SI；多目标分支；形式合成端点及引用前体明确作为边界。 |
| [Itomanallene B](../data/routes/paper-2d9b2cb848bfbd04/report.html) | 43 | 36 | 6 | 正文含实验，SI 为谱图；丙二烯轴手性另存，混合物中心未强行指定。 |
| [Palhinines B/C](../data/routes/paper-c68b92dcce0b5753/report.html) | 47 | 43 | 6 | 仅正文；B／C 与对映系列；酪氨酸上游文献步骤作为边界。 |
| [Mulberrofurans 等](../data/routes/paper-94a995685012cf20/report.html) | 27 | 24 | 10 | 正文＋SI；共同中间体与四个目标；消旋与部分中心未定，不纳入完整立体训练真值。 |
| [ent-Kaurane 系列](../data/routes/paper-561d3429850cabb7/report.html) | 54 | 51 | 10 | 仅 SI；多目标 ent-kaurane 网络；部分羟基、环氧与混合物立体待补。 |
| [Papililone A](../data/routes/paper-c4cb813fe92c2654/report.html) | 59 | 47 | 12 | 仅 SI；消旋／不对称路线及结构修订；提议结构与实得结构分开。 |
| [Breviones B/C/N](../data/routes/paper-d5b6a4cfeaa21ccf/report.html) | 60 | 57 | 11 | 仅 SI、部分覆盖；B／C／N 主线与模型；失败环扩张、37 对照及部分立体待补。 |
| [Mangicol D](../data/routes/paper-59ea1b0b856fb5d7/report.html) | 26 | 17 | 6 | 仅正文；骨架构建与结构修订；引用前体及部分多元醇构型仍有边界。 |
| [Strasseriolide A](../data/routes/paper-2ecc227214f2cf77/report.html) | 42 | 37 | 2 | 仅正文；两片段汇合与大环化；仅整理 Strasseriolide A，B 排除。 |
| [iso-Gladiolin methyl ester](../data/routes/paper-5ffc2379ff4366f0/report.html) | 24 | 20 | 3 | 仅正文含实验；片段汇合、22／24 元环混合物；合并收率保留原范围。 |
| [Schenck 级联四目标](../data/routes/paper-e1019ba02f1e20ab/report.html) | 46 | 43 | 20 | 正文＋SI；四个目标、失败前路与模型；假设机理中间体不计为实得产物。 |
| [Bacillosporin C](../data/routes/paper-920358bb74cd4159/report.html) | 33 | 36 | 17 | 仅 SI；上游、氧化二聚及具结构副产物；S7 图文不一致，消旋体为代表构型。 |
| [Stemocurtisine](../data/routes/paper-53d2449f553459cc/report.html) | 43 | 33 | 12 | 正文＋SI；消旋与早期富集系列；新生混合物／波浪键中心未指定。 |
| [Thelepogine](../data/routes/paper-85e8c2686b8db79f/report.html) | 51 | 40 | 9 | 正文＋SI；全路线、控制实验和结晶衍生物；丙二烯、二茂铁及季铵立体表示有边界。 |
| [Dibehenoyl-feruloyl glyceride](../data/routes/paper-7536ef37e89afbbd/report.html) | 27 | 17 | 11 | 仅 SI；天然甘油脂与衍生物；保护芳酸的上游制备缺失，区域异构体收率为混合范围。 |
| **合计** | **745** | **624** | **175** | 候选数据，待独立审核 |

## 数据与序列

- [SQLite 数据库](../data/atlas.sqlite)、[数据库总览](../data/database/report.html)
- [本批清单与校验计数](../data/extraction/twenty-paper-batch-20260910.json)、[逐篇 CSV](../data/extraction/twenty-paper-results-20260910.csv)
- [逐分子立体复核清单](../data/extraction/twenty-paper-stereo-review-20260910.jsonl)

可维护输入在 `data/facts/<paper_id>.json`，绑定来源在 `data/facts/sources/`。每篇的 `data/routes/<paper_id>/` 包含分子、反应、步骤、参与物和路线的 JSON／CSV，另有 SDF、SVG、HTML 和 SHA-256 校验清单。记录包含原文编号、canonical isomeric SMILES、分子式、证据页码／来源哈希、试剂、溶剂、收率及其作用范围。

`routes.json` 中的 `molecule_smiles_sequence`、`step_reaction_smiles_sequence` 保存依赖顺序；汇合路线同时读取 `reactant_labels`、`product_labels`、`ordered_event_ids`。这些不是未经验证的原子映射反应。原文没有画出的中间体用操作阶段表达；混合物／多步总收率不分配为各产物／单步收率。

立体复核 JSONL 对所有本批分子设置 `complete_stereo_training_eligible=false`，因为尚无独立化学准入；同时列出 RDKit 检测到的未指定潜在立体元素及来源限定。自动检测不能证明原文构型正确，也不能完整表达消旋样品、轴手性、丙二烯手性或金属配位。Mulberrofuran 等含未解决立体信息的条目未进入完整立体训练真值。

## 风险筛选与原文冲突

按用户要求及现有 [detail-policy](../data/extraction/detail-policy.json)，本次将 EBC-329、Schisanlactone A／Ganodermalactone H、Ussuriedine 相关论文改为仅保留文献信息，并以其他文章补足 20 篇。前两项依据正文报告的细胞毒性信号作保守排除；Ussuriedine 依据正文明确的 Veratrum 家族归属与项目已有排除规则，不声称已测得其特定毒性数值。替换过程见批次清单。Strasseriolide 仅纳入 A，没有提取 B 的合成详情。

筛选针对目标与文献范围，不是实验安全认证。来源中的危险操作提示保留为问题项。Macrocephadiolide 原始活性研究报告的是 NO 抑制，不能直接当作细胞毒性测定：[原始分离研究](https://pubs.rsc.org/en/content/articlelanding/2020/qo/d0qo00030b)。

收率、HRMS、编号、FeCl2／FeCl3 等图文矛盾按来源保存，未因程序检查通过而消除。甘油脂 SI 从本地 ZIP 提取，PDF SHA-256 与原索引成员一致；未重新下载或替换来源。薯蓣皂苷元对照的连接及已指定中心与 [PubChem CID 99474](https://pubchem.ncbi.nlm.nih.gov/compound/99474) 的 InChI 比对一致。

## 校验与数据库变化

- 全部 75 个案例通过格式、分子式、反应／路线拓扑、CSV 内容、SDF 往返和文件校验和检查：[案例审计](../data/extraction/case_audit.json)。
- 本批 745 条分子记录的实际 SDF 重新读入后，isomeric SMILES 均与 JSON 一致；检查未发现临时原子映射或意外自由基。
- SQLite 完整性、状态计数和 14 项数据库导出检查通过：[数据库验证](../data/extraction/database_validation.json)。
- 桥环 SDF、事实编译和既有案例的 12 项相关回归测试通过。Malbrancheamide 23 的默认二维 SDF 布局会丢失桥头立体信息，导出器现先检查往返，必要时采用 CoordGen；仍不一致则报错。

| 数据表 | 本批前 | 本批后 | 净增 |
|---|---:|---:|---:|
| papers | 133 | 133 | 0 |
| molecules | 1681 | 2377 | 696 |
| paper_compounds | 1475 | 2220 | 745 |
| reaction_events | 980 | 1604 | 624 |
| operation_steps | 1093 | 1717 | 624 |
| routes | 308 | 483 | 175 |

全库状态：75 篇候选提取、30 篇待结构转录、14 篇本地来源缺失、14 篇仅元数据，共 133 篇。

复现：使用 `.venv/Scripts/python.exe`，按批次清单的 20 个 ID 调用 `scripts/batch_extract_atlas.py --paper <id> ...`，再运行 `scripts/audit_route_cases.py`、`scripts/validate_atlas_database.py`。未变案例复用缓存；不要为了重现本批而强制重建全库。
