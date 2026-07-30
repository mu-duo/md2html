"""CLI 入口：md2html / m2h 命令。"""

import shutil
import sys
from pathlib import Path
from typing import List, Optional

import click

from .generator import generate
from .builder import build


def _resolve_mermaid_mode(mode: str) -> str:
    """解析 mermaid 自动模式：检测 mmdc 确定最终渲染模式。

    Args:
        mode: 原始模式值 ('auto', 'browser', 'png')

    Returns:
        解析后的模式 ('browser' 或 'png')
    """
    if mode != "auto":
        return mode

    if shutil.which("mmdc"):
        return "png"

    print("信息: 未检测到 mermaid-cli (mmdc)，将使用浏览器端渲染模式。"
          "安装 mmdc 可获得 PNG 预渲染: npm install -g @mermaid-js/mermaid-cli")
    return "browser"


@click.command()
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_dir', default=None,
              type=click.Path(), help='输出目录（缺省为 {输入名}_md2html）')
@click.option('--title', default=None, help='项目标题')
@click.option('--author', default=None, help='作者')
@click.option('--exclude', 'exclude_patterns', multiple=True,
              help='排除 glob 模式（可多次指定）')
@click.option('--force', is_flag=True, help='不询问直接覆盖已存在的输出目录')
@click.option('--skip-build', is_flag=True, help='跳过 Sphinx 构建')
@click.option('--mermaid-mode', type=click.Choice(['auto', 'browser', 'png']),
              default='auto',
              help='mermaid 渲染模式：auto=自动检测（默认），browser=浏览器渲染，png=mmdc 预渲染')
def main(
    input: str,
    output_dir: Optional[str],
    title: Optional[str],
    author: Optional[str],
    exclude_patterns: List[str],
    force: bool,
    skip_build: bool,
    mermaid_mode: str,
):
    """将 Markdown 文件或目录转换为 Sphinx singlehtml。

    INPUT 必须是存在的 .md 文件或目录。
    """
    input_path = Path(input).resolve()

    # 验证输入：必须是 .md 文件或目录
    if input_path.is_file():
        if input_path.suffix != '.md':
            print(f"错误: 输入文件必须是 .md 文件: {input_path}", file=sys.stderr)
            sys.exit(1)
        is_single_file = True
        input_stem = input_path.stem
    elif input_path.is_dir():
        is_single_file = False
        input_stem = input_path.name
    else:
        print(f"错误: 输入路径不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 解析 mermaid 自动模式
    mermaid_mode = _resolve_mermaid_mode(mermaid_mode)

    # 处理输出目录：缺省为当前目录下 {输入名}_md2html
    if output_dir is None:
        output_path = (Path.cwd() / f"{input_stem}_md2html").resolve()
    else:
        output_path = Path(output_dir).resolve()
        if output_path == input_path:
            print(f"错误: 输出目录不能与输入相同: {output_path}", file=sys.stderr)
            sys.exit(1)

    # 输出目录已存在时的处理
    _handle_existing_output(output_path, force)

    # 生成 Sphinx 项目
    generate(
        input_path=input_path,
        output_dir=output_path,
        title=title or "",
        author=author or "",
        exclude_patterns=list(exclude_patterns),
        is_single_file=is_single_file,
        mermaid_mode=mermaid_mode,
    )

    # 构建
    if not skip_build:
        build(output_path, mermaid_mode=mermaid_mode)


def _handle_existing_output(output_path: Path, force: bool):
    """处理已存在的输出目录：--force 静默覆盖，无 --force 时交互确认。

    非 TTY 环境下无 --force 时直接报错退出。
    """
    if not output_path.exists():
        output_path.mkdir(parents=True)
        return

    if not output_path.is_dir():
        print(f"错误: 输出路径已存在但不是目录: {output_path}", file=sys.stderr)
        sys.exit(1)

    contents = list(output_path.iterdir())
    if not contents:
        return  # 目录为空，直接使用

    if force:
        shutil.rmtree(output_path)
        output_path.mkdir(parents=True)
        return

    # 非 TTY：退化到旧行为，直接报错
    if not sys.stdin.isatty():
        print(f"错误: 输出目录非空: {output_path}。使用 --force 强制覆盖。",
              file=sys.stderr)
        sys.exit(1)

    # TTY：交互确认
    answer = input(f"输出目录已存在且非空: {output_path}\n是否覆盖？[y/N] ")
    if answer.strip().lower() == 'y':
        shutil.rmtree(output_path)
        output_path.mkdir(parents=True)
    else:
        print("已取消。", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
