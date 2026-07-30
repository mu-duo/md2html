"""构建器：调用 Sphinx 构建 singlehtml。支持 auto（自动检测）、browser（浏览器渲染）和 png（mmdc 预渲染）模式。"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 匹配 mermaid 代码块的模式
MERMAID_RE = re.compile(r'```\s*mermaid\b', re.IGNORECASE)


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

    output_path = output_dir / "build" / "singlehtml" / "index.html"
    print(f"构建完成: {output_path}")
