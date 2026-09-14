# 两篇新增文章的路线提取与 token 实测

本轮于 2026-09-09 10:30:04（Asia/Shanghai）开始。选择时，两篇均未有 `data/routes/<paper_id>/dataset.json`，且正文和补充材料已在本地；不占用原优先 19 篇的名单。

| 文章 | 分子记录 | 制备/对照事件 | 路径 | 报告 |
|---|---:|---:|---:|---|
| Fleminchalcone C，`paper-ed2bb8684ec5aaae` | 29 | 26 | 4 | [打开](../data/routes/paper-ed2bb8684ec5aaae/report.html) |
| Violaceoid E，`paper-c2d9ec46e06369bf` | 23 | 21 | 6 | [打开](../data/routes/paper-c2d9ec46e06369bf/report.html) |
| 合计 | 52 | 47 | 10 | |

这里的“事件”是有来源依据的制备或对照转换。一锅多阶段操作保留 `operation_stages`；未单独分离的内部中间体不补写独立 SMILES。路径包括成功路线和有图示产物的对照分支，不等于 10 个天然产物。

## 实际过程

1. 从库存及已有案例状态中选文，确认正文与 SI 的真实内容，排除重复正文和原始 NMR 压缩包。
2. 使用本地文件、已有索引、限量摘录和局部页图核对反应图。两篇原文下载次数为 **0**；计量接口说明另有官方文档查阅，不属于论文获取。
3. Fleminchalcone C 逐图转录共同骨架，程序展开外消旋体及两个对映体系列，按来源配置检查 CIP、环系、双键和分子式。
4. Violaceoid E 的制备步骤位于正文，SI 是谱图及计算。18 个实验标题名称与正文规范化匹配通过；连同 1 个从起始物图示整理的名称，共 19 个名称交给本地 OPSIN 一次批量解析。之后核对源图，不将名称解析成功等同于结构正确。
5. 两篇结构和反应事实保存在 `data/curation/*-network.json`。通用编译器生成 canonical isomeric SMILES、反应连接、路线序列、分子式和精确质量。43 条 HRMS 记录由程序抽取后按来源顺序绑定标签：42 条分子式一致，1 条保留原文冲突。
6. 程序生成 JSON、CSV、SDF、SVG 和 HTML，执行 schema、拓扑、canonical SMILES、端点、SDF 往返和校验和检查。仅重建选中的两篇；随后统一更新一次 SQLite 和数据库导出。
7. 重复运行相同选择，确认案例和数据库均命中缓存。过程包括试运行发现的问题和修正，它们也计入 token。

## 关键化学范围

- **Fleminchalcone C：**从已知 6 出发，外消旋路线 8 个事件、R/S 路线各 9 个事件；另含未保护底物的 Shi 对照。6 的文献上游六步不在本文制备网络内。外消旋物另存带 AND 组的 canonical CXSMILES；普通 canonical SMILES 不伪装成单一对映体。a/b 表示所报主要对映体，不表示 100% ee。
- **Violaceoid E：**覆盖原拟结构的短路线、修订天然结构 `(4R,5R)-1` 的 8 事件路线及另一条原拟结构路线；展开正文合并图中的分离中间体 18、19、20。3α/3β 的 68% 是混合物总产率，11/12 则分别保存实验所报分离产率。
- Violaceoid E 的金属烯醇盐 5 是机理中间体，13 是文献对照物，计算模型不是制备产物；均不列为本文分离节点。
- 原文用量、编号、ee 和 HRMS 冲突保留在 `issues`/`hrms_checks`。Violaceoid E 的 16 原文公式写 O₃，图示、名称和所报质量支持 O₄，两者分别记录。
- 两篇已覆盖上述**本文成功制备网络**。已知起始物的外部文献制备没有补造；`from_commercial_starting_materials_complete=false`。独立化学专家审核仍待完成，未进入正式 benchmark。

## Token 计量口径

权威数字见 [two-paper-token-usage.json](../data/extraction/two-paper-token-usage.json)，由 [计量程序](../scripts/measure_extraction_tokens.py)读取当前工作 turn 的本地 `token_usage_record` 实测记录。没有依据字数估算，也没有导出提示词、思维内容、其他 turn 数据或会话标识。

- `total`：运行时该 turn 的累计计数；`responses`：去重后的逐响应数字。`per_response_sum_matches_turn_total` 验证二者一致。
- `input_tokens` 已包含 `cached_input_tokens`；两者不能相加。非缓存输入另列 `uncached_input_tokens`。
- `reasoning_output_tokens` 是输出的子集，不能再次加到 `output_tokens` 上。
- `stages` 分为选文/计量准备、第一篇、第二篇、共享验证与交付。它按记录时间分段，跨工具边界和共享代码使其**不是两次隔离的单篇基准测试**；化学原文较简单也不代表共享计量开销小。
- 总数包含选文、技能与文档读取、计量工具开发、失败修正、两篇提取、验证和最终答复。确定性 Python/RDKit/OPSIN 程序本身没有调用 LLM；它们返回给助手的内容仍会占后续模型输入。
- 最后一个后台采集器等最终答复的用量落盘后补记。`turn_completed=true` 表示工作 turn 已结束；`measurement_finalized=true` 表示结束后至少 30 秒、记录至少 15 秒无新增，采集器已收尾。查看最终数值应检查这两个字段。
- 这是 token 遥测，不是账单金额。历史长上下文的缓存输入会重复计入每次响应输入；没有同条件对照，不能从本轮直接推算节省百分比。

## 复现

验收结果：27 个案例审计通过，其中 25 个复用既有审计缓存；SQLite 完整性通过、外键违规 0。流程与新案例测试 43 项通过，数据库与新案例测试 60 项通过（两组有 3 项重复）。第二次选文运行显示两个案例 `unchanged`、数据库 `unchanged`。

```powershell
.venv/Scripts/python.exe scripts/batch_extract_atlas.py --paper paper-ed2bb8684ec5aaae --paper paper-c2d9ec46e06369bf
.venv/Scripts/python.exe scripts/audit_route_cases.py
.venv/Scripts/python.exe -m pytest tests/test_two_paper_networks.py tests/test_extraction_cache.py tests/test_resource_cache.py tests/test_partial19_cases.py tests/test_batch_extraction.py -q
```

结构编译不依赖再次调用 OPSIN 或 LLM。源文件哈希、配置、程序、运行时和输出参与缓存判断；改变来源时要求重新核对。token 采集的本地日志定位信息留在 `.local/`，不属于可再分发数据。
