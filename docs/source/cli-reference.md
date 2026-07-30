# 命令行参考

## 用法

```
md2html [OPTIONS] INPUT
m2h [OPTIONS] INPUT
```

`m2h` 是 `md2html` 的等价别名，以下示例均可用 `m2h` 替代 `md2html`。

## 参数

### INPUT

输入路径，必须是已存在的 `.md` 文件或目录。

```bash
# 单文件
md2html README.md

# 目录
md2html ./docs
```

### `-o, --output`

输出目录（可选）。缺省时在当前目录下生成 `{输入名}_md2html`：

- 目录输入 `StaDoc` → 输出 `./StaDoc_md2html`
- 单文件输入 `README.md` → 输出 `./README_md2html`

显式指定 `-o` 时，直接使用指定的路径（不追加 `_md2html` 后缀）：

```bash
md2html ./docs -o ./my-output
```

目录处理规则：

- 不存在则自动创建
- 存在且为空则直接使用
- 存在且非空时：
  - `--force`：静默覆盖
  - 无 `--force`：交互式询问是否覆盖（非 TTY 环境下直接报错，需使用 `--force`）

```bash
md2html README.md                       # 输出到 ./README_md2html
md2html ./docs                          # 输出到 ./docs_md2html
md2html ./docs -o ./output              # 显式指定输出目录
md2html ./docs -o ./output --force      # 覆盖已有输出（不询问）
```

### `--title`

项目标题，显示在文档页面顶部。默认值：

- 目录输入：目录名
- 单文件输入：文件名（不含扩展名）

```bash
md2html ./docs --title "项目文档"
```

### `--author`

作者信息，显示在文档元数据中。默认为空。

```bash
md2html ./docs --author "张三"
```

### `--exclude`

追加排除 glob 模式，可多次指定。模式相对于输入根目录，匹配路径本身及其任一父目录。以 `/` 结尾仅匹配目录。

```bash
# 排除 drafts 目录
md2html ./docs --exclude 'drafts/'

# 排除多个模式
md2html ./docs --exclude 'drafts/' --exclude '*.tmp.md'
```

与 `.cripperignore` 规则叠加生效。详见[输入组织约定](conventions.md)。

### `--force`

存在同名输出目录时，不询问直接覆盖。不加 `--force` 时，终端环境下会提示 `是否覆盖？[y/N]`，非终端环境（管道、CI）下直接报错退出。

```bash
md2html ./docs --force
```

### `--skip-build`

只生成 Sphinx 项目（`source/`、`Makefile`、`make.bat`），不执行构建和清理。之后可在输出目录中运行 `make singlehtml` 手动构建。

```bash
md2html ./docs --skip-build
cd ./docs_md2html
make singlehtml
```

### `--mermaid-mode`

mermaid 图表的渲染模式，可选 `auto`（默认）、`browser` 或 `png`。

| | auto（默认） | browser | png |
|---|---|---|---|
| 行为 | 检测 mmdc：有→png，无→browser | 浏览器端渲染 | 构建期 mmdc 预渲染为 PNG |
| 依赖 | 可选 mmdc | 无 | mmdc 必需 |
| 渲染时机 | 自动选择 | 浏览器打开时 | 构建时 |
| 产物形态 | 自动选择 | HTML 内嵌 mermaid 库 | HTML + `_images/` 目录 |

**auto 模式**：自动检测系统是否安装了 `mmdc`。若检测到，使用 png 模式；若未检测到，打印信息提示后降级到 browser 模式。

**browser 模式**：mermaid 库内嵌在 HTML 中（约 3.3MB），浏览器打开时实时渲染。适合日常迭代和离线分发。

**png 模式**：在构建期将每张 mermaid 图预渲染为 PNG 图片。产物体积更小（约 2MB），适合最终定稿、打印导出。需要手动安装 mmdc：

```bash
npm install -g @mermaid-js/mermaid-cli
```

```bash
# 默认：自动检测
md2html ./docs

# 强制浏览器端渲染
md2html ./docs --mermaid-mode browser

# 强制 PNG 预渲染（需 mmdc）
md2html ./docs --mermaid-mode png
```

### `m2h` 别名

`m2h` 是 `md2html` 的等价别名，所有选项和行为完全一致：

```bash
m2h README.md
m2h ./docs -o ./output --force
m2h ./docs --mermaid-mode browser
```
