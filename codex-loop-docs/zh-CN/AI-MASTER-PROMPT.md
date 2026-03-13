# AI 固定提示词

在开始任何编码前，严格按以下顺序执行：
1. 重读用户原始文档，避免偏离方向。
2. 以 canonical 项目文档作为直接执行基底。
3. 检查 git 状态、分支、远端和未提交改动。
4. 依次读取 PROJECT-STATUS、PROJECT-HANDOFF、PROJECT-TODO、PROJECT-ROADMAP、PROJECT-DECISIONS、PROJECT-ACCEPTANCE。
5. 只选择依赖已满足的最小任务项。
6. 完成一个最小任务项后，先更新状态文档，再提交一次 git commit，commit message 必须包含任务 ID。
7. 若缺少工具链，优先自行补齐；只有补齐失败时才将任务标记为 blocked。
