# Prettier 配置说明

本项目已配置 Prettier 代码格式化工具，确保代码风格的一致性。

## 配置文件

- `.prettierrc` - Prettier 格式化规则配置
- `.prettierignore` - 忽略格式化的文件和目录
- `.vscode/settings.json` - VS Code 编辑器集成配置

## 可用命令

```bash
# 格式化所有文件
npm run format

# 检查代码格式（不修改文件）
npm run format:check

# 检查代码格式并显示结果
npm run lint
```

## VS Code 集成

如果您使用 VS Code，项目已配置：
- 保存时自动格式化
- Prettier 作为默认格式化工具
- 支持 TypeScript、React、JavaScript、JSON、CSS、HTML 等文件类型

## 格式化规则

- 使用单引号
- 行尾分号
- 2 个空格缩进
- 最大行宽 80 字符
- 尾随逗号（ES5 兼容）
- 箭头函数参数避免括号（单参数时）
