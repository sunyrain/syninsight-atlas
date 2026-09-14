# 按需取证与增量提取

默认输出仅保留案例动作、数据库动作和统计；完整案例日志位于 `.local/build-cache/<paper_id>.log`。

## 只处理选定文章

```powershell
.venv/Scripts/python.exe scripts/batch_extract_atlas.py --paper paper-c4c0d668b9a2b9f7 --paper paper-85ead15cb461d3b7
```

首次运行为选定案例建立缓存。后续比较源文件、适配器及本地导入依赖、引用的结构配置、模式文件、目录、Python/RDKit 版本和输出内容。未变化则跳过案例导出；缺失或损坏的输出会重新生成。失败运行不更新缓存。

`--rebuild-cases` 检查所有已注册案例，仍跳过有效缓存；`--force-cases` 强制重建所选案例；`--verbose` 显示完整日志。

数据库无输入变化且输出完好时，跳过 SQLite 与导出重建。有变化时，在所有选定案例完成后统一进行一次原子数据库重建，以维持全局分子去重和引用一致性；目前不是逐表 SQL 增量写入。

## 限量读取证据

```powershell
.venv/Scripts/python.exe scripts/source_excerpt.py ../papers/paper-c4c0d668b9a2b9f7/supporting_information/si-001.pdf --query 'compound 16' --limit 2 --chars 900
```

沿用按源文件 SHA256 缓存的 PDF 文本，输出匹配页码与限长片段。可用 `--pages 6 7` 指定页码。相同文件、页码、查询和限长请求再次执行时，仅提示已返回页码；确需重新阅读时加 `--repeat`。

缓存和限长只减少重复处理，不代替源图核对。名称候选、绘图立体化学、混合物与产率范围仍需分别判断。

## 下载资源与名称解析去重

`acquire_missing_sources.py` 的实际下载入口现在使用 `.local/http-cache/`。缓存按 URL 建索引，响应正文按 SHA256 共用文件；成功重定向的最终 URL 也可命中缓存。URL 的片段和主机大小写会规范化，查询参数不会重排，以保留签名语义。

- 普通成功响应缓存 1 天；PDF 缓存 30 天。
- 401/402/403 缓存 7 天；404/410 缓存 1 天；其他失败缓存 1 小时，避免无变化时反复重试。
- 命中时核对正文哈希，损坏缓存不会作为有效响应返回。
- 同一进程的并发线程共享同一 URL 的请求；不承诺多个独立进程之间只发一次请求。
- 下载仍受原有官方域名和内容校验约束。缓存只在本地；不会把已缓存的摘要视为全文。

`deterministic_batch_candidates.py` 的 `local_opsin(names, jar_path)` 现在读取缓存，只把新增名称交给 Java。成功、失败和解析警告均按 OPSIN JAR 哈希、版本和 RDKit 版本保存；已有未解析名称不会反复计算。它输出的仍是名称候选，不能自动认定与源图一致。

## 一条命令完成离线案例审计

```powershell
.venv/Scripts/python.exe scripts/audit_route_cases.py
.venv/Scripts/python.exe scripts/audit_route_cases.py --paper paper-c4c0d668b9a2b9f7
```

程序执行 schema、canonical SMILES、分子式、底物/产物连接、路线拓扑、JSON/CSV 一致性、SDF 往返和文件校验和检查，输出 `data/extraction/case_audit.json`。正常终端输出只有汇总和失败项。结果按案例文件、校验代码及运行时版本缓存；无变化时复用，`--force` 可强制复查。

这些步骤不调用 LLM，也不下载资源。原文冲突和未解决事件单独列出，检查通过不会升级全文覆盖或专家确认状态。代码外通过浏览器、搜索工具或手工调用第三方网站的请求不受此下载缓存管理。

## 当前资料阻塞

- Coniferin：正文未取得；糖供体 6、7 的确切结构不全。已有片段和终产物结构，糖基化缺口不作推定连接。
- Ternatusine：正文未取得；缺少保护步骤、环氧化物身份和部分后续转换；后段结构与 HRMS 分子式冲突。已提取三段可核对路线。

没有新增原文、补充材料或更正时，不重复尝试把这些缺口拼接成完整路线。新增来源后按原文重新核对，并更新对应配置与来源哈希。
