"""构建器：调用 Sphinx 构建 singlehtml。支持 auto（自动检测）、browser（浏览器渲染）和 png（mmdc 预渲染）模式。

构建成功后，将 singlehtml 产物平铺到输出根目录，清理 Sphinx 脚手架（source/、Makefile、make.bat、build/）。
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 匹配 mermaid 代码块的模式
MERMAID_RE = re.compile(r'```\s*mermaid\b', re.IGNORECASE)

# Sphinx 构建后不需要保留的内部文件/目录（相对于 singlehtml 目录）
_CLEANUP_INTERNAL = {'.doctrees', '.buildinfo', 'objects.inv'}


def _has_mermaid_blocks(source_dir: Path) -> bool:
    """扫描 source 目录下所有 .md 文件，检查是否包含 mermaid 代码块。"""
    for md_file in source_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        if MERMAID_RE.search(content):
            return True
    return False


def build(output_dir: Path, mermaid_mode: str):
    """在 output_dir 中运行 Sphinx 构建 singlehtml。

    Args:
        output_dir: 包含 source/ 目录的 Sphinx 项目根目录
        mermaid_mode: "browser" 或 "png"（auto 已在 CLI 层解析完毕）
    """
    # png 模式：验证 mmdc 可用（若不存在则在开始构建前直接报错）
    if mermaid_mode == "png":
        source_dir = output_dir / "source"
        if _has_mermaid_blocks(source_dir) and not shutil.which("mmdc"):
            print("错误: png 模式需要 mermaid-cli (mmdc)，但未找到。"
                  "请安装：npm install -g @mermaid-js/mermaid-cli",
                  file=sys.stderr)
            sys.exit(1)

    cmd = [
        sys.executable, "-m", "sphinx.cmd.build",
        "-b", "singlehtml",
        "source",
        "build/singlehtml",
    ]
    # PYTHONUTF8=1: 避免 sphinxcontrib-mermaid 的 Popen(text=True)
    # 在中文 Windows 上默认使用 GBK 编码而无法写入含 Unicode 的 mermaid 源码
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(cmd, cwd=str(output_dir), env=env)
    if result.returncode != 0:
        sys.exit(result.returncode)

    # 构建成功：扁平化 singlehtml 到输出根目录，清理脚手架
    _flatten_and_cleanup(output_dir)


def _flatten_and_cleanup(output_dir: Path):
    """将 build/singlehtml/ 的用户可见产物移动到输出根目录，删除其余一切。

    搬移：*.html, _static/, _images/ → output_dir/
    丢弃：.doctrees/, .buildinfo, objects.inv（Sphinx 内部文件）
    清理：source/, build/, Makefile, make.bat
    """
    singlehtml_dir = output_dir / "build" / "singlehtml"
    if not singlehtml_dir.is_dir():
        print(f"警告: 未找到构建产物目录: {singlehtml_dir}", file=sys.stderr)
        return

    # 1. 将用户可见文件搬移到输出根目录
    for entry in singlehtml_dir.iterdir():
        if entry.name in _CLEANUP_INTERNAL:
            continue
        dest = output_dir / entry.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(entry), str(dest))

    # 2. 删除整个 build/ 目录
    build_dir = output_dir / "build"
    if build_dir.is_dir():
        shutil.rmtree(build_dir)

    # 3. 删除 Sphinx 脚手架
    source_dir = output_dir / "source"
    if source_dir.is_dir():
        shutil.rmtree(source_dir)
    makefile = output_dir / "Makefile"
    if makefile.is_file():
        makefile.unlink()
    makebat = output_dir / "make.bat"
    if makebat.is_file():
        makebat.unlink()

    # 4. 查找并打印入口 HTML 路径
    html_files = list(output_dir.glob("*.html"))
    entry = html_files[0] if html_files else output_dir / "index.html"
    print(f"构建完成: {entry}")
