# 使用场景

## 1. 单文件快速分享

把一篇 Markdown 文档转成 HTML，发给同事。

```bash
md2html 设计文档.md -o ./output
```

将 `output/build/singlehtml/index.html`（连同 `_static` 目录）打包发送即可。对方浏览器打开即可阅读，无需安装任何工具。

## 2. 项目文档集构建

整个文档目录一键转成带章节导航的文档网站。

```bash
md2html ./docs -o ./output --title "项目文档"
```

- 用数字前缀控制章节顺序（如 `01-概述.md`、`02-安装.md`）
- 每章目录用 `index.md` 写章节概述
- 相对路径图片自动保留，无需额外处理

## 3. 离线 / 内网分发

默认 browser 模式的产物**完全离线可用**：

- 不引用任何 CDN 或外部 URL
- mermaid 渲染库已内嵌在 HTML 中
- 单文件拷到任何机器上，浏览器打开即可

内网环境、无网络访问的机器上都可以正常使用，mermaid 图也能正常渲染。

## 4. 打印导出 PDF

浏览器打开 singlehtml 后，使用浏览器的"打印 → 另存为 PDF"功能即可导出 PDF。

**建议**：

- 文档较长、图较多时，建议使用 png 模式再打印。浏览器端渲染的 SVG 图表在打印分页时可能不如 PNG 稳定
- 打印前等待页面完全加载，确认所有 mermaid 图都已渲染完成（红框占位表示渲染失败，检查方法见[常见问题](faq.md)）

```bash
# 先用 png 模式构建，再打印
md2html ./docs -o ./output --mermaid-mode png
# 浏览器打开 output/build/singlehtml/index.html
# 文件 → 打印 → 另存为 PDF
```