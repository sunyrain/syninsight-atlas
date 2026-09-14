# Epimedonins 与 Spermidines 来源核对案例

本轮新增两个可复现案例。数据均使用 RDKit 2026.03.6 的 canonical isomeric SMILES，
原子、键和来源立体信息来自原生 ChemDraw 对象；具名补充反应物另标记
`procedural_interpretation`。没有独立专家审定，`formal_benchmark_eligible=false`。

| 案例 | 分子记录 | 制备事件 / 操作组 | 目标路径 | 覆盖范围 |
| --- | ---: | ---: | ---: | --- |
| [Epimedonins A/B](../data/routes/paper-8c076c5cf883e668/report.html) | 16 | 11 / 11 | 3 | 正文 Scheme 1/2 与 SI 中绘出的正向制备网络 |
| [Spermidines](../data/routes/paper-12c087bbcec8cc4c/report.html) | 21 | 14 / 14 | 2 | 现有 SI 中全部制备，包括两种 NHS 酯；本地缺正文 |

“操作组”以来源报告的制备事件为边界。多阶段操作中未画出、未分离的内部中间体
不补写 SMILES；因此该计数不等于全部实验操作次数或全部微观化学步骤。
汇聚路线的分子序列是拓扑排序，相邻分子记录不一定直接反应；逐步连接请用
`step_reaction_smiles_sequence` 或底物/产物关联表。

## Epimedonins A/B

文献 DOI：`10.1021/acs.jnatprod.6c00751`。
正文文件 `article/main.pdf` 与实际为 DOCX 的 `supporting_information/si-003.zip`
均固定 SHA256。Word 嵌入对象 `word/embeddings/oleObject1.bin` 位于 XML 段落 62，
包含 16 个编号结构。分子绑定保存原生片段 ID、CDX 哈希和来源定位，实验信息
分别指向段落 66–96；正文证据指向第 3 页。

三条路径分别通往 Epimedonin A，以及经过碘代物 4 或三唑中间体 3 的 Epimedonin B。
原文逆合成 Figure 2 的编号 4 与正向 Scheme 2 不一致；数据采用正向编号，避免把
碘代物 4 与三唑化合物 15 合并。另保留底物名称误植、NMR 列表重复、时间和产率精度差异。

6 项 HRMS 分子式均与图结构一致，但化合物 4、15 的来源计算质量各偏高约 2 Da；
实测质量与结构计算值一致。来源数值不覆盖、不静默更正。验证结果见
[`hrms_checks.json`](../data/routes/paper-8c076c5cf883e668/hrms_checks.json)。

`full_article_route_coverage=true` 专指来源绘出的正向网络。E04 为先缩合后碘化的
两阶段制备，内部中间体未报告结构，因此
`all_internal_experimental_stage_structures_reported=false`。

## Spermidines

文献 DOI：`10.1002/slct.73435`。
来源为固定 SHA256 的 `supporting_information/si-001.docx`。
19 个分子由来源绘图提取，另有 NHS 与 CbzCl 两个由实验段落明确名称转换的反应物。
13 个编号共价母体均交叉核对汇总图与单步制备图，得到相同 canonical SMILES。
26 条原生关系包含汇总图与制备图重复；整理后为 14 个独立制备事件。

必须同时保留以下信息，不能只使用 SMILES 一列解释最终样品：

- 目标 1 的汇总图标 HCl，单步图标 HBr，元素分析公式含 Br。`salt_annotations`
  分别保存证据；`canonical_smiles` 是图中的共价母体，`isolated_form_smiles=null`。
- 化合物 7、11 图中标 HCl，但实验经过碳酸氢钠水洗并描述为粗油。保留来源冲突，
  不替作者推定最终质子化位点或盐计量。
- 目标 2 明确为外消旋体；普通 SMILES 不携带外消旋比例，`stereo_status` 保留此信息，
  不随意添加 `@`。来源画出的 E 双键予以保留。
- 目标 1 的天然/合成比较表给出双键耦合常数 12.5/15.7 Hz，并有碳位移差异；
  来源合成结构不等于已经独立确认天然样品身份。表头误用编号 13 的问题另存。
- 两种 NHS 酯的制备把氯化试剂写为 `COCl2`，但质量/物质的量不一致。
  该试剂 `normalized_smiles=null`，避免任意选择化学身份。
- “quantitative” 保留为定性产率；粗品质量不折算为不存在的分离产率。
  E01/E02/E05/E10 各包含两阶段制备，未绘出的内部结构不补写。

10 项 HRMS 以 `[M+H]+` 离子公式和质量核对全部通过；母体公式不因此增加 H。
分子式/质量一致不能证明连接方式、盐型或立体构型。详见
[`hrms_checks.json`](../data/routes/paper-12c087bbcec8cc4c/hrms_checks.json)。

本地缺正文，上游化合物 3 从来源给定起点开始。因此
`available_si_preparation_network_covered=true`，但 `full_article_route_coverage=false`。

## 输出与复现

每个 `data/routes/<paper_id>/` 目录提供 `dataset.json`、分子/事件/步骤/路线
JSON 与 CSV、`molecules.sdf`、结构 SVG、`report.html`、`validation.json` 和校验清单。
源文献图像、DOCX、CDX 与检查缓存保留在私有归档或 `.local/`，不随公开数据复制。

```powershell
.venv/Scripts/python.exe scripts/extract_epimedonins_case.py
.venv/Scripts/python.exe scripts/extract_spermidines_case.py
.venv/Scripts/python.exe scripts/batch_extract_atlas.py
.venv/Scripts/python.exe scripts/validate_atlas_database.py
.venv/Scripts/python.exe -m pytest tests/test_epimedonins_case.py tests/test_spermidines_case.py -q
```

来源文件哈希变化会终止案例编译，不能用旧绑定静默生成新数据。
数据库 `paper_compounds.metadata_json` 保留盐型、结构范围和立体说明；
`reaction_events.metadata_json` 保留定性产率、粗品质量及其他来源属性。
