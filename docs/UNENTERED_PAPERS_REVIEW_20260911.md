# 未入库文章全量复查（2026-09-11）

本次“未入库”指已有文献元数据、尚无已整理化学路线的 **44篇**。全部已记录处理结论：**2篇新增结构网络候选、29篇按保守风险范围排除、2篇风险依据仍待核、11篇原文证据不足**。

24篇既有风险决定经复核保留；18篇补查出版社、原始研究及可用作者／机构来源；另2篇此前合并任务被自动审查阻断，本次依据目标特异证据改为更窄的结构网络整理。未获得新的合成正文／SI PDF，新增候选使用的是本地已有来源。

不能据此称任何路线“绝对无风险”。低毒性或特定测试范围无细胞毒性不等于普遍安全；细胞筛选信号也不等于人体高毒性分级。两个新增案例仅收录源图分子、SMILES、证据页码和有向步骤连接，**不包含试剂、溶剂、收率、温度、时间或任何制备／生物实验流程**。

## 新增入库

| 案例 | 分子记录 | 步骤连接 | 路径 | 来源与主要边界 |
|---|---:|---:|---:|---|
| [Bisnicalaterines B/C](../data/routes/paper-96939387a0ca2d6e/report.html) | 38 | 25 | 9 | 仅SI的片段网络；3条缺底物身份的连接隔离，不生成反应SMILES。P/M及其他立体表示有限。 |
| [Ascidiathiazones A/B](../data/routes/paper-715f9106f76c8961/report.html) | 20 | 21 | 9 | 正文Schemes 2–4；SI为表征。硫立体尚未完整编码。 |

合计新增 **58条文章内分子记录、46个可表示的步骤连接、18条片段／分支路径**；另有3条未解析事件不进入反应SMILES或路线序列。SQLite去重分子净增50。数据库中的46条`operation_steps`在本批仅是图连接记录容器，不表示已提取实验操作或全部阶段；未填造实验阶段数。两个案例均显式保留`full_article_route_coverage=false`，不是两篇完整实验数据集，也未取得独立化学准入。

Bisnicalaterines 的G24–G26中，命名输入eburnamine 5尚无已绑定的确定结构，因此保留未解析事件，前段与末段分别建路径，没有删除该底物后伪装成单底物反应。B/C等P/M身份使用独立文献标签和`source_helicity`保存；普通SMILES相同不表示文献中的化合物身份相同。

Ascidiathiazones 的[出版社摘要](https://pubs.acs.org/doi/10.1021/acs.joc.6c00749)提到A此前测得的低毒性；该结论不自动覆盖所有衍生物。Bisnicalaterines 的[原始作者研究摘要](https://www.jstage.jst.go.jp/article/tennenyuki/52/0/52_151/_article/-char/en)区分了有细胞毒性的A与测试至50µM未见细胞毒性的B/C，不将A的风险外推到B/C。

此前自动审查拒绝的是合并详细提取任务，理由为潜在双重用途风险，并非毒理鉴定。本次仅完成上述收窄范围；原拒绝记录及范围变更保存在[策略历史](../data/extraction/detail-policy.json)，未将其删除或改写为“原任务通过”。

## 其余42篇的结论

风险排除共29篇，其中24篇保留既有决定，5篇新增：Menominins A/B、FR182877、erycristagallin、aigialomycin D和Litcubanine A。新增依据为目标特异的细胞增殖／细胞毒性结果，具体浓度、单位及限制保留在逐篇记录；不将其统称为高急性毒性。

风险待核2篇：8-methoxybicolosin C尚缺目标定量风险对应；Xestodecalactone A／(S)-Curvularin中，已查到curvularin的细胞毒性研究，但测试物与本文特定立体异构体的对应未完成独立结构核验。这两篇也缺足够本地合成原文，保留元数据并暂停详细提取。

其余11篇未找到足以支持完整结构网络的可用原文。4篇本地SI主要为谱图／分析数据，不能据此补造箭头；7篇仍缺有效本地合成全文。Lycodine文献被出版社标为综述，但本项目未将“综述”本身设为风险排除，当前实际阻碍仍是来源不足。Amycolamicin也是受限综述，不能用不同年份的论文冒充同一来源。

全部44篇的可筛选结论见[逐篇CSV](../data/extraction/unentered-review-results-20260911.csv)，完整证据与检索记录见[总清单JSON](../data/extraction/unentered-review-20260911.json)、[A组6篇](../data/extraction/unentered-review-a-20260911.json)、[C组7篇](../data/extraction/unentered-review-c-20260911.json)及[另外5篇来源复查](../data/extraction/unentered-review-root-20260911.json)。此前受限访问缓存被保留，未绕过登录或访问限制，也未向作者发送请求。

## 数据与验证

- [SQLite数据库](../data/atlas.sqlite)、[数据库总览](../data/database/report.html)
- [逐步SMILES表](../data/database/route_steps.csv)、[路线SMILES序列表](../data/database/route_smiles.csv)
- [实际SDF回读检查](../data/extraction/unentered-sdf-qa-20260911.json)、[逐分子立体复核边界](../data/extraction/unentered-stereo-review-20260911.jsonl)
- [来源分类更正](../data/extraction/unentered-source-corrections-20260911.json)：Ascidiathiazones误标的11页SI实际为正文副本；真实SI为82页文件。仅修正元数据，原PDF未改动。

全库91个案例确定性审计通过，数据库一致性与导出校验通过；新增58条SDF记录实际重新读入后与JSON的isomeric SMILES一致。另核验所有新增事件及步骤均没有实验条件／收率字段值。编译器仅修正结构网络类别的范围说明传递，防止步骤导出误显示默认的制备操作说明。

这些检查验证格式、结构图、分子式、拓扑、序列和导出一致性，不证明所有立体信息已正确完整，也不代替独立化学审查。Ascidiathiazones的20分子／21箭头另经内部代理对照原图复核；仍不算外部化学准入。

| 数据表 | 复查前 | 复查后 | 净增 |
|---|---:|---:|---:|
| papers | 133 | 133 | 0 |
| molecules | 2925 | 2975 | 50 |
| paper_compounds | 2829 | 2887 | 58 |
| reaction_events | 2156 | 2202 | 46 |
| operation_steps | 2269 | 2315 | 46 |
| routes | 617 | 635 | 18 |

复现：仅对新增候选的两个paper ID运行`batch_extract_atlas.py --paper`，随后运行`audit_route_cases.py`及`validate_atlas_database.py`。全库状态：{"extracted_candidate_pending_review": 91, "metadata_only": 31, "pending_structure_transcription": 4, "source_missing_local": 7}。
