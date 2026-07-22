"""CLI 入口：md2html 命令。"""

import shutil
import sys
from pathlib import Path
from typing import List, Optional

import click

from .generator import generate
from .builder import build


@click.command()
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_dir', default=None,
              type=click.Path(), help='输出目录（缺省为当前目录下以输入名命名的目录）')
@click.option('--title', default=None, help='项目标题')
@click.option('--author', default=None, help='作者')
@click.option('--exclude', 'exclude_patterns', multiple=True,
              help='排除 glob 模式（可多次指定）')
@click.option('--force', is_flag=True, help='强制覆盖非空输出目录')
@click.option('--skip-build', is_flag=True, help='跳过 Sphinx 构建')
@click.option('--mermaid-mode', type=click.Choice(['browser', 'png']),
              default='browser',
              help='mermaid 渲染模式：browser=浏览器端渲染（默认），png=构建期 mmdc 预渲染为 PNG')
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
    elif input_path.is_dir():
        is_single_file = False
    else:
        print(f"错误: 输入路径不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 处理输出目录：缺省为当前目录下以输入名命名（单文件取 stem，目录取目录名）
    if output_dir is None:
        default_name = input_path.stem if is_single_file else input_path.name
        output_path = (Path.cwd() / default_name).resolve()
        if output_path == input_path:
            # 缺省输出与输入相同（如 md2html ./docs），自动加后缀避免污染/误删输入
            output_path = (Path.cwd() / f"{default_name}-html").resolve()
            print(f"提示: 缺省输出目录与输入相同，改用 {output_path}")
    else:
        output_path = Path(output_dir).resolve()
        if output_path == input_path:
            print(f"错误: 输出目录不能与输入相同: {output_path}", file=sys.stderr)
            sys.exit(1)
    if output_path.exists():
        if not output_path.is_dir():
            print(f"错误: 输出路径已存在但不是目录: {output_path}", file=sys.stderr)
            sys.exit(1)
        # 检查是否为空
        contents = list(output_path.iterdir())
        if contents:
            if force:
                # 清空目录
                shutil.rmtree(output_path)
                output_path.mkdir(parents=True)
            else:
                print(f"错误: 输出目录非空: {output_path}。使用 --force 强制覆盖。",
                      file=sys.stderr)
                sys.exit(1)
    else:
        output_path.mkdir(parents=True)

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


if __name__ == '__main__':
    main()