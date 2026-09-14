# 白藜芦醇二聚体：端到端提取记录

本轮新增论文 `paper-d035a83486621e1f`，*Biomimetic Radical Oligomerization Enables the Total Synthesis of Five Resveratrol Dimers*，DOI `10.1021/acs.orglett.6c01391`。

已完成源文件核对、结构转录、事实配置、标准格式导出及 SQLite 入库。新增 **29 个文章内分子记录、25 个反应事件、26 个操作阶段、12 条路径**，包含五个目标产物及对照/替代路线。它们仍是待独立化学审核的候选数据，不能作为已经完成专家确认的基准真值。

## 查看和使用

- [交互式案例报告](../data/routes/paper-d035a83486621e1f/report.html)
- [完整数据集 JSON](../data/routes/paper-d035a83486621e1f/dataset.json)
- [分子表和 canonical isomeric SMILES](../data/routes/paper-d035a83486621e1f/molecules.csv)
- [逐步反应表](../data/routes/paper-d035a83486621e1f/reactions.csv)
- [按依赖顺序排列的路线及 SMILES 序列](../data/routes/paper-d035a83486621e1f/routes.json)
- [分子结构 SDF](../data/routes/paper-d035a83486621e1f/molecules.sdf)
- [可维护的事实配置](../data/facts/paper-d035a83486621e1f.json)
- [统一 SQLite 数据库](../data/atlas.sqlite)
- [案例审计](../data/extraction/case_audit.json)；[数据库审计](../data/extraction/database_validation.json)

JSON 中保留分子身份、原文编号、底物/产物角色、试剂、溶剂、产率范围、操作阶段、证据页码和源文件 SHA-256。RDKit 版本为 `2026.03.6`。相对构型代表 SMILES 必须连同 `stereo_status`、`stereo_note` 使用；不要将其解释成已确认的绝对构型。反应没有生成未经验证的原子映射。

## 目标路线

| 目标 | 原文编号 | 反应事件序列（包括必要的并行前体支路） |
|---|---|---|
| δ-viniferin | 2 | E03 → E05；E10 → E11 → E12；E13 → E14 |
| gnetin C | 4 | E01；E10 → E11 → E12；E16 → E18 |
| ampelopsin B | 8 | E01；E10 → E11 → E12；E16 → E17 |
| ε-viniferin | 3 | E03 → E05 → E06 → E07；E10 → E11 → E12；E19 → E21 → E22 |
| ampelopsin F | 9 | E01；E10 → E11 → E12；E16 → E24 → E25 |

路径中的分号表示前体支路，不表示省略步骤。完整双底物和产物对应关系见反应表；多底物合成不应被误读为单条线性分子链。另有直接单甲磺酰化、热反应替代方案及保护基/区域异构体对照路径。

## 覆盖范围与未解决项

正文共 6 页，补充材料共 59 页。核对范围为正文 Figures 2–4 与 SI 2.1–2.8 的制备网络；全文制备边界已覆盖，但不是从商业原料开始的全部历史合成。SI p4 的两个前体引用既往文献，本文没有提供其上游步骤，数据不补猜这些步骤。正文机理图中的自由基、共振形式、过渡态不作为已分离制备中间体。

- SI 多次复用 S1、S2，目录与实际标题的目标编号亦有差异，已用独立 ID 区分。
- 原文存在产率、试剂、时间及浴温描述差异，全部保留为来源冲突；未把两步总产率分摊到单步。
- 18 是 1:1 非对映异构体混合物，89% 为混合物产率；19 是混合粗品的 qNMR 产率，不能视为纯品分离产率。
- DHB 楔形键按相对构型表示；ampelopsin F 及其保护体 35、36 的桥环连接关系已编码，但透视图的立体构型尚未完整编码。这是本例距离完整立体化学真值仍存在的明确缺口。
- SI 中部分 HRMS 分子式、质量和物质的量存在明显不一致。转录结构经分子式检查通过，不等于原文数值冲突已经消失。

## 风险筛选

本轮沿用 [detail-policy.json](../data/extraction/detail-policy.json)，其中 8 篇排除文章仅保留元数据。选文初筛参考 [Gnetin C 人体研究](https://pubmed.ncbi.nlm.nih.gov/31234376/) 与 [寡聚芪活性研究](https://pubmed.ncbi.nlm.nih.gov/19280145/)，未将本例目标归入高效毒素合成任务。这个决定不意味着全部中间体、试剂或实验过程无风险，也不是覆盖整个文献库的毒理认证。

## 复现

在仓库根目录执行：

```powershell
.venv/Scripts/python.exe scripts/fact_case.py build --paper paper-d035a83486621e1f
.venv/Scripts/python.exe scripts/batch_extract_atlas.py --paper paper-d035a83486621e1f
.venv/Scripts/python.exe scripts/audit_route_cases.py
.venv/Scripts/python.exe scripts/validate_atlas_database.py
```

源文件绑定已保存，不要在来源变化时直接重新绑定；应先重新核对变化页。源文、页面图与结构回绘 QA 位于 `.local/`，不随公共数据包分发。事实配置是后续修改入口，导出文件由既有编译器生成。
