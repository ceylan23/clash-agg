# clash-agg

把三个 Clash 订阅（存在仓库 Secrets 里，不写在代码中）定时合并成一个聚合订阅：

- 每 6 小时自动刷新一次，也可在 Actions 页手动 Run workflow
- 输出文件：`out/all.yaml`，里面只有一个名为「聚合」的 select 总组，包含全部节点（节点名带 [1]/[2]/[3] 来源前缀）
- 聚合订阅链接（raw）：
  `https://raw.githubusercontent.com/ceylan23/clash-agg/main/out/all.yaml`

## 需要在仓库设置里添加的 Secrets

Settings → Secrets and variables → Actions → New repository secret，共三个：

- `SUB_URL_1`
- `SUB_URL_2`
- `SUB_URL_3`

## 注意

- 本仓库是公开的：任何人打开仓库都能看到合并后的节点列表并使用这些节点。订阅原始链接只存在 Secrets 里，不会出现在代码和输出中。
- 这份聚合配置是全流量走所选单节点的极简规则（MATCH,聚合），适合给自动化脚本切换节点用；日常上网请勿把它当主力配置长期使用，或在 Clash Verge 里单独建一个配置档切换使用。
