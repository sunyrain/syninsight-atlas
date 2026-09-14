# 更新现有 GitHub 仓库与部署

目标仓库：https://github.com/sunyrain/syninsight-atlas

此上传包按现有仓库的根目录布局组织。不要新建仓库，不要在已有仓库中重新运行 `git init`，也不要将 ZIP 文件本身当作网页内容上传。

## 更新步骤

1. 用 GitHub Desktop 打开或克隆 `sunyrain/syninsight-atlas`，先同步远程最新状态。
2. 将增量 ZIP 解压到该仓库根目录，让 `index.html` 与已有 `data/`、`assets/`、`scripts/` 同级。ZIP 内没有外层目录。合并目录并覆盖同名更新文件，不要删除其他已有文件。
3. 查看变更清单并提交、Push。包中保留了原有导出脚本、发行校验器、测试、许可、引用信息及原始发现数据。
4. GitHub Pages 使用仓库根目录作为发布源；若已有站点配置正常，可保持该配置。新配置时在 Settings → Pages 选择 Deploy from a branch、实际发布分支及 /(root)。仓库没有提交 Pages workflow；本包没有擅自添加部署工作流。

既有站点：https://sunyrain.github.io/syninsight-atlas/

对已有本地仓库，复制文件后可执行：

```sh
git status --short
git diff --stat
python scripts/validate_release.py
python scripts/validate_web.py
git add .
git commit -m "Add desktop reaction dataset and connected pathway viewer"
git push
```

约 41 MiB 的 `data/atlas.sqlite` 超过网页上传的 25 MiB 单文件限制，推荐 GitHub Desktop 或 Git 推送。包内文件均小于 100 MiB。

## 本地预览与构建

已生成的页面直接使用 `python -m http.server 8765` 预览。需要重建时安装 `requirements-web.txt` 并执行 `python scripts/build_web.py`；运行测试则安装 `requirements-test.txt` 后执行 `python -m pytest tests/test_release.py tests/test_web.py`。

`export_from_autoplanner.py` 保留原仓库用途，需要原始上游工作区；它不是网站更新所必需的步骤，不应为刷新网页而重新导出原始发现快照。

## 文件校验

`CHECKSUMS.sha256` 保留原有文件范围，按 Git 中原始数据的实际字节修复换行符造成的哈希偏差，验证原始发现快照；新增数据由其自身校验与网站校验覆盖。增量 ZIP 的 SHA-256、变更清单与本次验证报告放在 ZIP 旁边，避免把机器特定上传说明或临时审核产物混入仓库。

官方参考：
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
