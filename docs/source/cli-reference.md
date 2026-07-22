# 命令行参考

## 用法

```
md2html [OPTIONS] INPUT
```

## 参数

### INPUT

输入路径，必须是已存在的 `.md` 文件或目录。

```bash
# 单文件
md2html README.md -o ./output

# 目录
md2html ./docs -o ./output
```

### `-o, --output`

输出目录（可选）。缺省时使用当前目录下以输入名命名的目录：

- 目录输入 `input/StaDoc` → 输出 `./StaDoc`
- 单文件输入 `README.md` → 输出 `./README`
- 若缺省目录与输入本身相同（如 `md2html ./docs`），自动改用 `./docs-html` 并打印提示；显式 `-o` 指定与输入相同的目录会报错（防止 `--force` 误删输入）

目录处理规则：

- 不存在则自动创建
- 存在且为空则直接使用
- 存在且非空则报错退出，使用 `--force` 强制覆盖

```bash
md2html input/StaDoc                # 输出到 ./StaDoc
md2html ./docs                      # 与输入同名，输出到 ./docs-html
md2html ./docs -o ./output          # 显式指定输出目录
md2html ./docs -o ./output --force  # 覆盖已有输出
```

### `--title`

项目标题，显示在文档页面顶部。默认值：

- 目录输入：目录名
- 单文件输入：文件名（不含扩展名）

```bash
md2html ./docs -o ./output --title "项目文档"
```

### `--author`

作者信息，显示在文档元数据中。默认为空。

```bash
md2html ./docs -o ./output --author "张三"
```

### `--exclude`

追加排除 glob 模式，可多次指定。模式相对于输入根目录，匹配路径本身及其任一父目录。以 `/` 结尾仅匹配目录。

```bash
# 排除 drafts 目录
md2html ./docs -o ./output --exclude 'drafts/'

# 排除多个模式
md2html ./docs -o ./output --exclude 'drafts/' --exclude '*.tmp.md'
```

与 `.cripperignore` 规则叠加生效。详见[输入组织约定](conventions.md)。

### `--force`

强制覆盖非空输出目录。**注意**：输出目录中的内容会被清空，手动修改会丢失。

```bash
md2html ./docs -o ./output --force
```

### `--skip-build`

只生成 Sphinx 项目（`source/`、`Makefile` 等），不执行编译。之后可在输出目录中运行 `make singlehtml` 手动构建。

```bash
md2html ./docs -o ./output --skip-build
cd ./output
make singlehtml
```

### `--mermaid-mode`

mermaid 图表的渲染模式，可选 `browser`（默认）或 `png`。

| | browser（默认） | png |
|---|---|---|
| 依赖 | 无 | mmdc (`npm install -g @mermaid-js/mermaid-cli`) |
| 渲染时机 | 浏览器打开时 | 构建时 |
| 速度 | 快（构建不耗时） | 慢（每图约 30 秒） |
| 产物形态 | 单个 HTML，内嵌 mermaid 库（约 3.5MB） | HTML + `_images/` 目录（约 2MB） |
| 适用场景 | 日常迭代、离线分发 | 最终定稿、需要 PNG 图片 |

```bash
# 默认：浏览器端渲染
md2html ./docs -o ./output

# 构建期预渲染为 PNG
md2html ./docs -o ./output --mermaid-mode png
```

png 模式需要 mmdc 可用。如果未安装，工具会报错并提示安装命令。无 mermaid 内容的文档即使选 png 模式也不需要 mmdc。