# 常见问题

## 1. mermaid 图显示红框占位

浏览器打开文档后，某些 mermaid 图显示为红框并附带错误信息，这是工具的**渲染失败兜底**机制。

**常见原因与修复**：

**标签含特殊字符**：`()`、`[]`、`{}` 等字符在 mermaid 语法中有特殊含义。如果标签文本需要包含这些字符，用双引号包裹：

```mermaid
# 错误：括号被解析为语法
graph LR
    A[AND(P0..P3)] --> B

# 正确：双引号包裹
graph LR
    A["AND(P0..P3)"] --> B
```

**嵌套方括号**：
```mermaid
# 错误
A[A[0]] --> B

# 正确
A["A[0]"] --> B
```

**参与者名撞保留字**：sequence 图中，参与者名不能与 mermaid 保留关键字冲突（如 `opt`、`loop`、`alt` 等，大小写不敏感）。使用别名解决：

```mermaid
# 错误：OPT 撞保留字 opt
sequenceDiagram
    participant OPT as OptFlow
    SM->>OPT: 调用

# 正确：用别名
sequenceDiagram
    participant OPTF as OptFlow
    SM->>OPTF: 调用
```

修改后重新构建即可。

## 2. LaTeX 数学公式不渲染

md2html 支持 `$...$`（行内）和 `$$...$$`（块级）LaTeX 数学公式，通过 MathJax 在浏览器端渲染。若公式显示为原始文本：

- **语法检查**：确保使用 `$...$`（行内）或 `$$...$$`（块级）定界符。不支持 `\(...\)`、`\[...\]` 或 `\begin{equation}` 等 LaTeX 环境语法
- **浏览器兼容**：MathJax 支持所有现代浏览器。若公式不渲染，检查浏览器是否禁用了 JavaScript
- **网络环境**：MathJax 从 CDN 加载（`cdn.jsdelivr.net`），需要网络连接。离线环境下公式会显示为原始 LaTeX 代码

```markdown
行内公式：$E = mc^2$

块级公式：

$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

## 3. png 模式报错缺少 mmdc

```
错误: png 模式需要 mermaid-cli (mmdc)，但未找到。
请安装：npm install -g @mermaid-js/mermaid-cli
```

`--mermaid-mode png` 需要在构建期把 mermaid 图渲染为 PNG，这依赖 mmdc 工具。mmdc 是 Node.js 工具，且需要 Chromium 浏览器。

安装步骤：

```bash
# 安装 mmdc（需要 Node.js 环境）
npm install -g @mermaid-js/mermaid-cli

# mmdc 还需要 Chromium，首次运行会自动下载
# 如果下载失败，可手动安装 Chromium 并设置环境变量：
# export PUPPETEER_EXECUTABLE_PATH=/path/to/chromium
```

**提示**：默认的 `auto` 模式会自动检测 mmdc。未安装 mmdc 时自动降级到 browser 模式，无需手动切换。

## 4. 页面没出现或顺序不对

**页面没出现**：检查是否被排除规则命中。隐藏文件、`__pycache__` 等会被自动排除；检查 `.cripperignore` 和 `--exclude` 参数。

**顺序不对**：文档顺序由文件名排序决定。建议使用数字前缀，如 `00-`、`01-`。

**章节首页被替换**：如果目录下有 `index.md` 或 `README.md`，它们会作为该章节的首页，其他 md 文件作为子页面。如果没有，工具会自动生成以目录名为标题的占位首页。

## 5. 产物使用问题

**直接打开 HTML 文件**：在输出目录中找到 `.html` 文件（如 `index.html`），双击即可在浏览器中打开。

**拷贝分发**：HTML 文件依赖 `_static/` 目录中的 CSS 和字体文件，**必须一起拷贝**。建议打包整个输出目录。

**浏览器兼容性**：支持所有现代浏览器（Chrome、Firefox、Edge、Safari 最新版本）。

**输出目录结构**：构建完成后，输出目录仅包含最终产物（HTML + `_static/` + `_images/`（如有））。Sphinx 脚手架（`source/`、`Makefile`、`make.bat`）已在构建后自动清理。如需保留脚手架，使用 `--skip-build` 仅生成不构建。

## 6. png 模式很慢

png 模式每张 mermaid 图需要独立启动一个 Chromium 实例来渲染，消耗约 30 秒/张。57 张图的文档可能需要约 30 分钟。

**建议**：

- 日常迭代使用默认 `auto` 模式（有 mmdc 时自动用 png，无则用 browser）
- 需要快速预览时用 `--mermaid-mode browser`（构建秒级完成）
- 最终定稿或需要打印输出时，再用 `--mermaid-mode png` 出正式版
- 如果文档不含 mermaid 图，任何模式速度相同

## 7. mermaid auto 模式的行为

`auto` 是默认模式，行为如下：

- 检测到 `mmdc` 已安装 → 使用 png 模式（构建期预渲染为 PNG）
- 未检测到 `mmdc` → 打印提示信息，自动降级到 browser 模式（浏览器渲染）

提示信息示例：

```
信息: 未检测到 mermaid-cli (mmdc)，将使用浏览器端渲染模式。
安装 mmdc 可获得 PNG 预渲染: npm install -g @mermaid-js/mermaid-cli
```
