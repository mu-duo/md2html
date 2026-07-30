# md2html

把 Markdown 文件或整个 Markdown 文档目录，转成带目录导航的**单页 HTML 文档**。mermaid 图表和 LaTeX 数学公式开箱即用。

## 特性

- **单文件或目录输入**：一篇 md 或整个项目文档集，一键构建
- **自动目录结构**：子目录自动成为章节，文件名排序决定顺序
- **mermaid 自动渲染**：自动检测 mmdc，有则 PNG 预渲染，无则降级到浏览器端渲染
- **LaTeX 数学公式**：支持 `$...$`（行内）和 `$$...$$`（块级），通过 MathJax 渲染
- **离线可用**：browser 模式下不依赖任何 CDN 或外部资源
- **干净输出**：构建后仅保留最终产物，无 Sphinx 脚手架残留

## 安装

需要 **Python >= 3.9**：

```bash
pip install /path/to/md2html
```

可选依赖（PNG 渲染 mermaid 图表）：

```bash
npm install -g @mermaid-js/mermaid-cli
```

## 快速开始

```bash
# 单文件
md2html 文档.md

# 整个文档目录
md2html ./docs

# 指定输出目录
md2html ./docs -o ./output

# 强制覆盖已有输出
md2html ./docs --force

# 指定 mermaid 渲染模式
md2html ./docs --mermaid-mode browser
```

`m2h` 是 `md2html` 的等价别名：

```bash
m2h README.md
```

## 命令参考

```
md2html [OPTIONS] INPUT
```

| 选项 | 说明 |
|------|------|
| `-o, --output` | 输出目录（默认 `{input}_md2html`） |
| `--title` | 文档标题 |
| `--author` | 作者信息 |
| `--exclude` | 排除 glob 模式（可多次指定） |
| `--force` | 强制覆盖已有输出目录（不询问） |
| `--skip-build` | 只生成 Sphinx 项目，不构建 |
| `--mermaid-mode` | 渲染模式：`auto`（默认）、`browser`、`png` |

## 输入组织

```
mydocs/
├── 00-overview.md          # 概述
├── 01-concepts.md          # 基本概念
├── 02-details/
│   ├── index.md            # 章节首页
│   ├── algo.md
│   └── images/
│       └── flow.png
└── 03-reference.md         # 参考
```

- 子目录 → 章节，文件名排序 → 页面顺序
- 数字前缀控制排序（`00-`, `01-`, ...）
- `index.md` / `README.md` 自动作为章节首页
- 图片相对路径自动保留
- 通过 `.cripperignore` 和 `--exclude` 排除文件

## 输出结构

构建完成后输出目录仅包含最终产物：

```
README_md2html/
├── README.html
├── _static/
└── _images/       ← png 模式下
```

## License

Apache-2.0
