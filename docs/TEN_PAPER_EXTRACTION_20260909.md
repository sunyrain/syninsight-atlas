# 十篇逐步路线提取（2026-09-09）

本批为此前尚无案例数据的十篇文章建立了来源绑定的候选路线，已统一导入 `data/atlas.sqlite`。新增 **240 条文章内分子记录、179 个制备事件、179 个操作组、58 条路线**。全部分子标识使用 RDKit canonical isomeric SMILES；混合物、未指定立体中心、合并收率和来源矛盾均保留。制备事件可以包含多个实验阶段，因此不能把事件数量直接当作作者声称的线性总步数。

这是候选提取完成，仍待独立化学专家复核。`full_article_route_coverage` 表示下表所声明边界内的正向路线覆盖，不代表补全了未获得的 SI、引用文献中的上游路线或未画出的瞬态中间体。

| 文章/目标 | 分子记录 | 制备事件 | 路线 | 主要边界 |
|---|---:|---:|---:|---|
| [Procerones A/B](../data/routes/paper-77fd7065d0ee2310/report.html) | 17 | 10 | 4 | 对映体分离明确标记为物理分离；混合物收率不分摊 |
| [Scytonemin / reduced scytonemin](../data/routes/paper-6ff9a985e64e1b0e/report.html) | 16 | 18 | 4 | 从已知底物出发；保留正文/SI 收率冲突和氧化还原互变 |
| [Waltherione S 及衍生物](../data/routes/paper-4535edb11a27941f/report.html) | 43 | 28 | 13 | 覆盖正文系列；羟基吡啶/吡啶酮互变异构不自动合并 |
| [Penibruguieramine A](../data/routes/paper-5adb96be45d961bc/report.html) | 18 | 10 | 2 | 成功路线与外消旋探索支线；引用的已知手性原料为边界 |
| [Spirobroussonin B](../data/routes/paper-3e14822739da3f53/report.html) | 13 | 10 | 7 | 电化学条件、异构体分离及放大实验；原文质谱计算值异常保留 |
| [Nobilin D / Combretastatin / Moscatilin / Erianin](../data/routes/paper-e33dda994e3c8017/report.html) | 27 | 21 | 11 | 包含失败氧化支线及表征衍生物；5/6/7 的相对立体化学仍待核对 |
| [PM100618 / PM110049](../data/routes/paper-77c5a5f42c45c029/report.html) | 27 | 20 | 3 | 两片段汇聚、E/Z 混合物及分离支线；分析性降解不计入制备网络 |
| [Isoriccardin C/D](../data/routes/paper-07ff316d638655e4/report.html) | 25 | 18 | 3 | 包含硝基类似物；SI 不可用，S1–S4 的上游制备不外推 |
| [Protulactone B](../data/routes/paper-7cb3eccb7d7bacf1/report.html) | 13 | 9 | 2 | 商购糖起始的八事件目标路线及甲醇解支线；异头体混合物不指定单一构型 |
| [Kayeassamin A / Mammeasin A](../data/routes/paper-e5ffb08ae89e3c60/report.html) | 41 | 35 | 9 | 成功路线、区域选择性失败支线及回收副产物；重复条件筛选不伪造新反应步骤 |

初选的 Daphnepapytone A 因笼状结构的立体化学仍需更充分核对，替换为 Isoriccardin C/D；前者保持未完成，未计入这十篇。

## 验证与数据库结果

- 新流程及相关缓存/既有案例检查首轮 17 项通过；数据库与批次检查 73 项通过；新增页面去重后相关 7 项再次通过。不同轮次存在重叠，不把它们相加当作独立测试数。
- [案例审计](../data/extraction/case_audit.json)：37 篇全部通过，27 篇沿用未变更的审计缓存。包括规范化 SMILES、分子式、拓扑、JSON/CSV/SDF 一致性和文件校验和。
- 新批次有 25 条直接来源绑定的 HRMS 检查：Procerones 8、Spirobroussonin 5、Protulactone 9、Kayeassamin/Mammeasin 3。计算值矛盾不会因分子式匹配而自动解决，其余分子式检查可能来自图形原子计数，不能宣称是独立 HRMS 证据。
- SQLite 外键和完整性检查通过；累计 1,067 条文章内分子记录、682 个制备事件、795 个操作组、200 条路线。全库唯一分子记录 1,316 条，含其他候选来源，不能与文章内记录直接相加。
- 133 篇状态：37 篇候选提取待复核、74 篇待结构转录、14 篇缺少本地来源、8 篇仅元数据。独立验证完整路线仍为 0。

## 本次落实的优化

1. `scripts/prepare_case_review.py` 以来源 SHA 保存私有审阅包。使用 PDF 内容流顺序读取，避免按坐标逐行排序混合相邻双栏；保留原始页文本。
2. 只折叠有明确 HRMS 终止标记且不跨实验段落的完整 NMR 数值块；不跨页猜测边界。折叠规则变更时重用已缓存原文，避免重新解析 PDF。
3. 页面图片已经缓存时不再打开 PDF；同页文本按内容哈希记录已读状态，重复输出默认省略，`--repeat` 可显式复核。
4. 系统命名解析交给带缓存的本地 OPSIN。Protulactone 的十个名称一次调用解析，后续重用；结构仍与原图和质谱核对。
5. 同一通用编译器完成 canonical SMILES、分子式、负离子质谱计算、导出及验证。补充芳香环数量约束，防止片段拼接环编号冲突造成分子式相同但连接错误。
6. 十篇案例集中入库一次。实测复跑：十篇均为 `unchanged`，数据库也为 `unchanged`，未重建既有案例或数据库。

[审阅包指标](../data/extraction/ten-paper-review-metrics-20260909.json)记录 14 个本地 PDF 来源，原始文本 590,711 字符，压缩文本 522,090 字符，减少 **11.62%**；本批未下载新来源。这里统计的是审阅包字符，**不是整轮 token 的节省比例，也不是计费量**。

## 重现

以 [批次清单](../data/extraction/ten-paper-batch-20260909.json) 中的十个 `paper_id` 调用批处理，每个 ID 使用一个 `--paper` 参数。公共 `data/curation/*-network.json` 保存化学整理结果，适配器调用同一个编译器；无需运行私有临时构建脚本。

```powershell
$batch = Get-Content data/extraction/ten-paper-batch-20260909.json -Raw | ConvertFrom-Json
$batchArgs = @('scripts/batch_extract_atlas.py')
foreach ($paper in $batch.papers) { $batchArgs += @('--paper', $paper.paper_id) }
& .venv/Scripts/python.exe @batchArgs
.venv/Scripts/python.exe scripts/audit_route_cases.py
```

准备、有限页阅读及图形渲染：

```powershell
.venv/Scripts/python.exe scripts/prepare_case_review.py --paper paper-7cb3eccb7d7bacf1
.venv/Scripts/python.exe scripts/prepare_case_review.py --paper paper-7cb3eccb7d7bacf1 --source-sha e3b5bca9bd3e9f4e64fa6b6a07a1544e708462edaabd6d5cabe3fe56693eedcd --read 6 7
.venv/Scripts/python.exe scripts/prepare_case_review.py --paper paper-7cb3eccb7d7bacf1 --source-sha e3b5bca9bd3e9f4e64fa6b6a07a1544e708462edaabd6d5cabe3fe56693eedcd --render 3
```
