# 输入组织约定

## 目录到文档树的映射

md2html 会把输入目录的层级结构映射为文档的章节结构：

- 每个子目录成为一个**章节**
- 目录下的所有 `.md` 文件是该章节的页面
- 章节内的页面按**文件名排序**

### Landing 页

每个目录需要一个"首页"来承载章节标题和子页面目录。查找规则：

1. 优先 `index.md`
2. 其次 `README.md`
3. 都没有时，自动生成一个占位页，标题为目录名

> 建议：需要自定义章节首页时，创建 `index.md` 并写入章节概述。

## 数字前缀控制顺序

章节和页面按文件名排序，因此建议使用数字前缀：

```
mydocs/
├── 00-overview.md          # 概述
├── 01-sta-concepts.md      # 基本概念
├── 02-graph.md             # 时序图
├── 03-delay-calc.md        # 延迟计算
└── 04-parasitics.md        # 寄生参数
```

数字前缀确保顺序稳定，不受后续增删文件影响。

## 图片与资源

整树拷贝输入目录，Markdown 中引用的相对路径图片会被原样保留。例如：

```markdown
![架构图](images/architecture.png)
```

只要 `images/architecture.png` 在输入目录中，构建后引用依然有效。

## 排除规则

以下规则按优先级叠加，决定哪些文件/目录不参与构建：

### 1. 内置默认排除

以下内容**始终排除**，无需配置：

- 隐藏文件和目录（以 `.` 开头，如 `.git`、`.cripperignore`）
- `__pycache__` 目录
- 名为 `build` 或 `_build` 的目录
- 名为 `conf.py`、`Makefile`、`make.bat` 的文件
- `*.pyc` 文件

### 2. `.cripperignore` 文件

在输入根目录下创建 `.cripperignore`，每行一个 glob 模式：

```
# 排除增量构建目录
IncrementalDocs/

# 排除草稿文件
drafts/*.md
```

以 `#` 开头的行为注释，空行忽略。模式匹配相对路径及其任一父目录。以 `/` 结尾仅匹配目录。

### 3. `--exclude` 命令行参数

可通过 `--exclude` 追加额外的排除规则，语法与 `.cripperignore` 相同：

```bash
md2html ./mydocs -o ./output --exclude 'drafts/' --exclude '*.tmp.md'
```

`--exclude` 可多次指定，与 `.cripperignore` 的规则叠加生效。

## 示例

假设输入目录结构如下：

```
mydocs/
├── .cripperignore
├── 00_overview.md
├── 01_concepts.md
├── 02_details/
│   ├── index.md
│   ├── algo.md
│   └── images/
│       └── flow.png
└── 03_reference.md
```

构建后文档结构为：

```
输出目录/
├── source/                    # 生成的 Sphinx 源文件
│   ├── 00_overview.md
│   ├── 01_concepts.md
│   ├── 02_details/
│   │   ├── index.md          # 作为章节首页
│   │   ├── algo.md
│   │   └── images/
│   │       └── flow.png      # 图片原样保留
│   ├── 03_reference.md
│   └── index.md              # 自动生成（根目录无 index.md/README.md）
├── build/singlehtml/
│   └── index.html            # 最终产物
├── Makefile
└── make.bat
```

- `02_details/index.md` 中会自动追加该章节的 toctree
- 根目录自动生成 `index.md`（标题为目录名 "mydocs"），可通过 `--title` 自定义
- 排除规则命中的文件不会出现在输出中