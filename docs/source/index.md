# md2html 用户指南

md2html（别名 `m2h`）是一个命令行工具，把 Markdown 文件或整个 Markdown 文档目录，转成带目录导航的**单页 HTML 文档**。mermaid 图表和 LaTeX 数学公式开箱即用。

## 特性

- **单文件或目录输入**：一篇 md 或整个项目文档集，一键构建
- **自动目录结构**：子目录自动成为章节，文件名排序决定顺序，`index.md`/`README.md` 自动作为章节首页
- **mermaid 自动渲染**：默认自动检测 mmdc，有则用 PNG 预渲染，无则降级到浏览器端渲染；也可显式指定模式
- **LaTeX 数学公式**：支持 `$...$`（行内）和 `$$...$$`（块级）LaTeX 数学公式，通过 MathJax 渲染
- **离线可用**：browser 模式下产物不依赖任何 CDN 或外部资源，拷走即看；png 模式下 mermaid 图表内嵌为图片
- **干净输出**：构建完成后仅保留最终产物（HTML + 静态资源），无 Sphinx 脚手架残留
- **别名支持**：`m2h` 是 `md2html` 的等价简写

## 安装

要求 **Python >= 3.9**。建议在虚拟环境中安装：

```bash
python3 -m venv venv
source venv/bin/activate
pip install /path/to/md2html
```

安装后即可使用 `md2html` 或 `m2h` 命令。

### 可选依赖

mermaid 图表默认自动检测 mmdc，若存在则优先使用 PNG 预渲染模式。安装 mmdc：

```bash
npm install -g @mermaid-js/mermaid-cli
```

未安装 mmdc 时，自动降级到浏览器端渲染模式（零额外依赖）。

## 快速开始

### 单个 Markdown 文件

```bash
md2html 文档.md
```

输出目录 `文档_md2html/` 中：
- `文档.html` —— 最终的单页 HTML 文档
- `_static/` —— CSS、JS、字体等静态资源
- `_images/` —— PNG 模式下 mermaid 预渲染的图片（browser 模式下可能不存在）

### 整个文档目录

```bash
md2html ./mydocs
```

输出目录 `mydocs_md2html/`，输入目录中的所有 `.md` 文件会被组织成带章节导航的文档集。

### 指定输出目录

```bash
md2html ./mydocs -o ./output
```

### mermaid 示例

文档中的 mermaid 代码块会被自动渲染为图表：

```mermaid
graph LR
    A[开始] --> B[处理]
    B --> C{判断}
    C -->|是| D[完成]
    C -->|否| B
```

### LaTeX 数学公式示例

行内公式：`$E = mc^2$`

块级公式：

$$ 
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
