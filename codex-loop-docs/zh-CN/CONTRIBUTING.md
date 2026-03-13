# 贡献说明

## 开发环境

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

## 规则

- 保持 CLI 跨平台。
- 将生成文档视为稳定模板，有意识地演进。
- 在可行范围内保留与现有 shell-loop 行为的一致性。
- 用户可见行为变化时，同步更新英文和中文文档。
