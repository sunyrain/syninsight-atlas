# 最后30篇天然产物路线整理（2026-09-10启动，2026-09-11收尾）

本批30篇均已记录处理结论：**14篇生成候选数据、10篇按风险范围排除、4篇缺少足够制备原文、2篇被自动安全审查阻断**。不是30篇完整提取成功。

新增 **609条文章内分子记录、552个反应事件、552条操作组记录、134条路线分支**，已写入SQLite；全库去重分子净增548。多个候选仍有缺失支线或未明确立体中心，不能直接当作完整立体化学训练真值。

## 候选数据

| 案例 | 分子 | 事件 | 路线 | 来源与限制 |
|---|---:|---:|---:|---|
| [Tuliposides](../data/routes/paper-33bf034f0faef47b/report.html) | 18 | 15 | 5 | 仅SI，DOCX经只读转换绑定PDF；名称与多步收率冲突保留。 |
| [Scandine](../data/routes/paper-d644e28e46d9de75/report.html) | 24 | 25 | 5 | 仅正文；消旋代表构型；交叉审核后补8个对照／优化事件，SI支线仍缺。 |
| [Allocyclinones A/B](../data/routes/paper-d137f8265a6d2e32/report.html) | 34 | 29 | 4 | 仅SI，两目标汇合路线；半缩酮构型未指定，未虚构S10，S4为分析性氘代实验。 |
| [Hinckdentine A](../data/routes/paper-02468cd0966939d2/report.html) | 71 | 74 | 19 | 四代路线与所得支线；44的C7构型已纠正；SI扩展范围及部分立体信息见问题清单。 |
| [Grisemycin](../data/routes/paper-d9dcbe7ff94b3396/report.html) | 23 | 18 | 1 | 部分立体覆盖；早期桥环中心待复核，混合收率及源文冲突保留。 |
| [Pensubrubine／propellane](../data/routes/paper-0e05697c35b4bd20/report.html) | 10 | 7 | 1 | 仅正文化学主线；缺SI、酶促范围及酯化支线；后续更正的影响未核实。 |
| [Streptospherin A](../data/routes/paper-30d3cf1b14fd5066/report.html) | 89 | 75 | 15 | 仅SI；已补模型表全部条目及6个Mosher双酯；早期辅助基／醇醛等中心待复核。 |
| [Pleuromutilin](../data/routes/paper-6a63c9306e309ac6/report.html) | 30 | 22 | 6 | 正文＋真实100页SI；6页审稿文件已纠正分类；冲突与立体边界见案例。 |
| [Exiguamines](../data/routes/paper-16903c93b7961b97/report.html) | 72 | 69 | 12 | 正文＋部分SI；部分C7及消旋体系的立体表示仍有限定。 |
| [Scholarisines](../data/routes/paper-6fb246fd524d3d54/report.html) | 22 | 26 | 5 | 正文＋SI；24/26的硫立体描述待定，25为引用前体边界。 |
| [Euphopia B](../data/routes/paper-9575513b24b2c4f6/report.html) | 36 | 36 | 7 | 正文＋SI；17b图文双键位置、收率和条件冲突保留。 |
| [Benthol A 片段](../data/routes/paper-cb317959e8cba4c0/report.html) | 126 | 106 | 36 | 本文报道A/B/B′片段及衍生物；最终天然产物组装属于配套论文。 |
| [Stephadiamine](../data/routes/paper-2d6f8f626286ab28/report.html) | 36 | 35 | 13 | 正文＋SI；消旋系列，部分笼状及过氧化物中心待复核。 |
| [Owerreine](../data/routes/paper-f6b5505f9a462a36/report.html) | 18 | 15 | 5 | 仅正文；公开SI下载返回403，尚未本地绑定，上游SI前体未纳入；部分新中心及暂定29待复核。 |

绑定来源：仅正文3篇、仅SI 3篇、正文和SI均有绑定8篇。“绑定两种来源”不等于两者完整覆盖；逐篇机器标志、遗漏说明与原始问题见[批次清单](../data/extraction/thirty-paper-batch-20260910.json)及案例报告。

## 未进行详细入库的16篇

| 文献 | 结论 | 依据或缺口 |
|---|---|---|
| Mansonone F | 风险范围排除 | 原始研究报告Mansonone F细胞毒性信号；按用户保守范围排除。 |
| Calothrixin B | 风险范围排除 | 原始研究中母体Calothrixin B有亚微摩尔细胞生长抑制信号。 |
| Cephalotaxine | 风险范围排除 | SI明确提出本路线叠氮化物操作使用防爆屏的安全警告。 |
| Shearilicine | 风险范围排除 | 正文报告低微摩尔细胞毒性信号。 |
| Tryptamine pyrroloindolines | 风险范围排除 | 目标集合包含原始药理证实的致惊厥calycanthine。 |
| Halenaquinone 等 | 风险范围排除 | 多目标范围中有亚微摩尔细胞毒性；不将该结论外推至所有成员。 |
| Cribrostatin 4 | 风险范围排除 | 正文明确细胞毒性并引用原始生物研究；5.01µM的原始全文未直接核验，数值不作为独立核实结果。 |
| Folicangine 等 | 风险范围排除 | 多目标中的voafolidine/isovoafolidine有细胞毒性依据，不将数值外推至全部目标。 |
| Curcusone I | 风险范围排除 | SI明确提示该路线特定中间体潜在爆炸风险。 |
| Psychotrimine／Psychotetramine | 风险范围排除 | 原始生物评价有低微摩尔细胞生长抑制信号。 |
| Shancigusins C/D | 来源不足 | 可用SI仅有谱图／表征，缺少足够路线或制备步骤；正文获取未成功，未据谱图猜造反应。 |
| Inonophenols A/B | 来源不足 | 可用SI仅有谱图／表征，缺少足够路线或制备步骤；正文获取未成功，未据谱图猜造反应。 |
| MK7607 | 来源不足 | 可用SI仅有谱图／表征，缺少足够路线或制备步骤；正文获取未成功，未据谱图猜造反应。 |
| Triplinones A/O | 来源不足 | 可用SI仅有谱图／表征，缺少足够路线或制备步骤；正文获取未成功，未据谱图猜造反应。 |
| Ascidiathiazones | 安全审查阻断 | 并行任务被自动安全审查以潜在双重用途风险中止，未重试详细提取；不等同于已证明目标有高毒性。 |
| Bisnicalaterines | 安全审查阻断 | 并行任务被自动安全审查以潜在双重用途风险中止，未重试详细提取；不等同于已证明目标有高毒性。 |

排除依据、页码、来源哈希和主文／原始研究引用保存在[详细范围策略](../data/extraction/detail-policy.json)及批次清单。细胞毒性筛选按用户保守范围执行，不能直接解释为人体系统毒性分级。原先14篇本地来源缺失的记录不属于本次最后30篇，仍保留原状态。

## 数据使用与校验

- [SQLite数据库](../data/atlas.sqlite)、[数据库总览](../data/database/report.html)、[逐步反应CSV](../data/database/route_steps.csv)、[路线SMILES序列CSV](../data/database/route_smiles.csv)
- [本批逐篇结果CSV](../data/extraction/thirty-paper-results-20260910.csv)、[逐分子立体复核JSONL](../data/extraction/thirty-paper-stereo-review-20260910.jsonl)、[实际SDF往返检查](../data/extraction/thirty-paper-sdf-qa-20260910.json)

每篇`data/routes/<paper_id>/`含分子、反应、操作组、参与物和路线的JSON/CSV，以及SDF、SVG、HTML和SHA-256校验清单。`routes.json`保存`molecule_smiles_sequence`与`step_reaction_smiles_sequence`；汇合路线结合`reactant_labels`、`product_labels`和`ordered_event_ids`读取。未画出的中间体不补造，多阶段操作保存在`operation_stages`内；操作组记录数不等于所有化学操作阶段数。多步与混合收率保留来源限定。可维护事实输入在`data/facts/`，来源绑定在`data/facts/sources/`。

5份Word SI经只读转换为带真实页码的PDF，保留原文件和转换provenance；Pleuromutilin的审稿文件已与真实实验SI分开登记。[源文件更正记录](../data/extraction/thirty-source-corrections-20260910.json)。未修改源PDF／DOCX内容。

全部89个现有案例的确定性审计通过，本批609条实际SDF记录重新读入后的isomeric SMILES与JSON一致，SQLite与数据库导出验证通过。此次未修改化学编译器。上述检查验证格式、图连通性、分子式、序列拓扑和导出一致性，不代替独立化学审查；本批完整立体训练准入仍为0。

| 数据表 | 本批前 | 本批后 | 净增 |
|---|---:|---:|---:|
| papers | 133 | 133 | 0 |
| molecules | 2377 | 2925 | 548 |
| paper_compounds | 2220 | 2829 | 609 |
| reaction_events | 1604 | 2156 | 552 |
| operation_steps | 1717 | 2269 | 552 |
| routes | 483 | 617 | 134 |

全库状态：{"extracted_candidate_pending_review": 89, "metadata_only": 26, "pending_structure_transcription": 4, "source_missing_local": 14}。

复现时仅将本批`completed`中的ID作为`batch_extract_atlas.py --paper`参数；该脚本同时更新全库inventory和SQLite。未获得facts的排除／阻断项不是可运行的化学适配器。随后运行`audit_route_cases.py`及`validate_atlas_database.py`，复用未变案例缓存。
