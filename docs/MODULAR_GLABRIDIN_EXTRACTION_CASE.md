# 模块化 Glabridin 的逐步路线案例

[`paper-64cf72c50cdd94d5`](../data/routes/paper-64cf72c50cdd94d5/report.html)
整理了现有 SI 第 2 节的 35 个分子记录、26 个制备事件、27 个操作组与 3 条路径：
(-)-Glabridin、经 SEM 保护路线得到的 (+)-Glabridin，以及 TBDMS 路线中发生部分消旋的产物 18。
另保留 rac-6 对照制备事件。正文缺失，SI 第 3 节优化筛选与第 4/5 节失败方案不计入成功路线。

本例与另一篇 `paper-0bac8bc7088bc164` 的 Glabridin 合成是不同文献；编号和来源证据
按文章隔离，相同 canonical isomeric SMILES 可复用全局分子身份，但不会合并实验或样品。

## 结构与来源

来源为 `supporting_information/si-001.docx`，SHA256：
`dc199fa6d1b22776047d6c76aee36277e2609f88933d5df179df2511c4651881`。

30 个分子记录来自原生 ChemDraw 分子图；s1、s2 和丙酮由 Word EMF 来源图转录，
另有丙二酸二乙酯和乙酸乙烯酯两个具名反应物。原生图引用保存 OLE 成员路径、
CDX 哈希及片段 ID；EMF 引用保存媒体成员字节哈希和 XML 段落。文件变化会阻止旧绑定复用。

全部分子通过 RDKit canonical isomeric SMILES 与 SDF 往返校验。22 项 HRMS 按
`[M+H]+` 或 `[M+Na]+` 的离子公式与质量核对通过。23a/23a′ 只有一次混合物 HRMS，
数据不把它算作两次独立结构确认。公式和质量一致不能证明立体纯度。

## 必须保留的来源区别

- 二醇在其制备中标作 5，在后续酰化图中标作 7；两处原生图一致。
  以 5 为数据编号，保存 `source_label_aliases=["5","7"]`，不造出一条 5→7 反应。
- 13a/13a′、17a/17a′、23a/23a′ 分别保存带来源立体标记的 SMILES。
  后续还原实验使用混合物，`reactant_relationship` 明确为非对映体混合物，
  并非两种底物互相偶联；reaction SMILES 不声明原子配平或化学计量。
- 18 的图画出正对映体，但来源说明其发生部分消旋。与 2 相同的绘图 SMILES
  不表示两个样品等同；`stereo_status` 保留部分消旋，`reported_ee_percent=null`。
  不用旋光度比值代替未报告的 ee。6 的来源 HPLC 报告 98% ee，单独保存。
- 成环步骤 E25 的单步图把醛写为 22，实验段落写为 23；根据汇总图与醛结构，
  反应物对应 4。汇总图的 48% 与单步图/实验的 45% 冲突；保留实验的 25% 和 20%。
- E17 图中写 >90%，实验写 80% 且质量不一致；保留报告的 80%，不计算替代产率。
  SEM 脱保护 E23 使用制备报告的 70%，不替换为筛选表的更高产率。
- E04 中原图明确画出的括号碘代物保存为 `s4-I`，拆为两个操作节点。
  回收的 s3（41%）另存 `recovered_compounds`，不当作碘代物转化的主产物。
- E02、E05、E15、E18 的内部结构未绘出时保持组合步骤；E18 的 16%/11% 为
  从 16 开始的两阶段总产率，不归给未编号醛的单步成环。

所有案例记录仍为 `pending_independent_chemist_review`，
`full_article_route_coverage=false`、`formal_benchmark_eligible=false`。
`available_si_preparation_network_covered` 的范围由 `coverage_definition` 限定为 SI 第 2 节。

## 复现与查询

```powershell
.venv/Scripts/python.exe scripts/extract_modular_glabridin_case.py
.venv/Scripts/python.exe scripts/batch_extract_atlas.py
.venv/Scripts/python.exe scripts/validate_atlas_database.py
.venv/Scripts/python.exe -m pytest tests/test_modular_glabridin_case.py -q
```

逐步序列见 [`routes.json`](../data/routes/paper-64cf72c50cdd94d5/routes.json)，
分子和事件的完整来源属性见 [`dataset.json`](../data/routes/paper-64cf72c50cdd94d5/dataset.json)。
SQLite 的 `paper_compounds.metadata_json` 保留样品立体信息和编号别名，
`reaction_events.metadata_json` 保留混合物投料语义、总产率范围及回收组分。
