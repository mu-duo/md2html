"""生成器：拷贝输入文件、排除规则、生成 toctree、conf.py、Makefile 等。"""

import fnmatch
import os
import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

# 内置默认排除规则
BUILTIN_EXCLUDES = [
    # 隐藏文件/目录
    lambda p, is_dir: any(part.startswith('.') for part in p.parts),
    # __pycache__
    lambda p, is_dir: any(part == '__pycache__' for part in p.parts),
    # build / _build 目录
    lambda p, is_dir: is_dir and p.name in ('build', '_build'),
    # conf.py / Makefile / make.bat
    lambda p, is_dir: not is_dir and p.name in ('conf.py', 'Makefile', 'make.bat'),
    # *.pyc
    lambda p, is_dir: not is_dir and p.name.endswith('.pyc'),
]

# 匹配 toctree 块的正则
TOCTREE_RE = re.compile(r'```\{toctree\}(.*?)```', re.DOTALL)
# 匹配 toctree 条目行（非空、非以 : 开头）
TOCTREE_ENTRY_RE = re.compile(r'^\s*([^\s:][^\s]*)\s*$')


def _read_ignore_patterns(input_root: Path) -> List[str]:
    """读取输入根目录下的 .cripperignore 文件，返回全局排除模式列表。"""
    ignore_file = input_root / '.cripperignore'
    patterns = []
    if ignore_file.is_file():
        with open(ignore_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns


def _match_pattern(rel_path: str, is_dir: bool, pattern: str) -> bool:
    """检查相对路径是否匹配某个排除模式。
    
    pattern 可带尾部 / 表示仅匹配目录。
    匹配规则：相对路径本身或其任一父目录匹配 fnmatch 模式即命中。
    """
    is_dir_pattern = pattern.endswith('/')
    pat = pattern.rstrip('/')

    # 检查路径本身及所有父目录
    check = rel_path
    while True:
        if fnmatch.fnmatch(check, pat):
            if is_dir_pattern and not is_dir:
                return False
            return True
        if check in ('', '.'):
            break
        check = str(Path(check).parent)
        if check == '.':
            if fnmatch.fnmatch('.', pat):
                if is_dir_pattern and not is_dir:
                    return False
                return True
            break
    return False


def _should_exclude(rel_path: Path, is_dir: bool, extra_patterns: List[str]) -> bool:
    """综合判断一个相对路径是否应被排除。"""
    # 内置规则
    for rule in BUILTIN_EXCLUDES:
        if rule(rel_path, is_dir):
            return True
    # 额外模式（.cripperignore + CLI --exclude）
    for pattern in extra_patterns:
        if _match_pattern(str(rel_path), is_dir, pattern):
            return True
    return False


def _copy_tree(src: Path, dst: Path, extra_patterns: List[str]):
    """递归拷贝 src 到 dst，应用排除规则。"""
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        rel = entry.relative_to(src)
        if _should_exclude(rel, entry.is_dir(), extra_patterns):
            continue
        if entry.is_dir():
            _copy_tree(entry, dst / rel.name, extra_patterns)
        else:
            dst_dir = dst / rel.parent
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry, dst / rel.name)


def _find_landing(dir_path: Path) -> Optional[Tuple[str, Path]]:
    """在目录中查找 landing 文档。返回 (类型, 路径) 或 None。
    
    类型: 'index', 'readme', None
    """
    index_md = dir_path / 'index.md'
    if index_md.is_file():
        return ('index', index_md)
    readme_md = dir_path / 'README.md'
    if readme_md.is_file():
        return ('readme', readme_md)
    return None


def _extract_toctree_entries(content: str) -> List[str]:
    """从文件内容中提取所有已存在的 toctree 条目。"""
    entries = []
    for match in TOCTREE_RE.finditer(content):
        block = match.group(1)
        for line in block.split('\n'):
            m = TOCTREE_ENTRY_RE.match(line)
            if m:
                entries.append(m.group(1))
    return entries


def _get_required_entries(dir_path: Path, subdirs: List[str]) -> List[str]:
    """获取某目录 toctree 应包含的全部条目。
    
    返回条目列表：本目录其他 .md 文件（按文件名排序）+ 各子目录 landing（按目录名排序）。
    条目格式为不含扩展名的相对路径（对子目录为 "dirname/landing_stem"）。
    """
    entries = []

    # 本目录其他 .md 文件
    md_files = []
    for f in sorted(dir_path.iterdir()):
        if f.is_file() and f.suffix == '.md' and f.name not in ('index.md', 'README.md'):
            md_files.append(f.stem)
    entries.extend(sorted(md_files))

    # 子目录
    for sd in sorted(subdirs):
        subdir_path = dir_path / sd
        landing = _find_landing(subdir_path)
        if landing:
            landing_type, _ = landing
            landing_stem = 'index' if landing_type == 'index' else 'README'
        else:
            landing_stem = 'index'  # stub 将生成 index.md
        entries.append(f"{sd}/{landing_stem}")

    return entries


def _append_toctree_entries(file_path: Path, missing_entries: List[str]):
    """在文件末尾追加包含缺失条目的 toctree 块。"""
    if not missing_entries:
        return
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write('\n\n```{toctree}\n:maxdepth: 2\n')
        for entry in missing_entries:
            f.write(f"{entry}\n")
        f.write('```\n')


def _generate_stub_index(dir_path: Path, title: str, entries: List[str]):
    """生成 stub index.md。"""
    content = f"# {title}\n\n"
    content += "```{toctree}\n:maxdepth: 2\n"
    for entry in entries:
        content += f"{entry}\n"
    content += "```\n"
    index_path = dir_path / 'index.md'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _generate_toctrees(source_dir: Path, root_title: str):
    """递归生成所有目录的 toctree。
    
    对每个目录：
    1. 确定 landing 文档
    2. 如果是 stub，生成 stub index.md
    3. 如果是已有 index.md/README.md，扫描已有 toctree 并追加缺失条目
    """
    def _process_dir(dir_path: Path, title: str):
        # 收集子目录名
        subdirs = sorted([d.name for d in dir_path.iterdir() if d.is_dir()])
        # 收集其他 .md 文件（排除 landing）
        md_files = sorted([
            f.stem for f in dir_path.iterdir()
            if f.is_file() and f.suffix == '.md' and f.name not in ('index.md', 'README.md')
        ])

        # 构建所需条目
        required = []
        required.extend(md_files)
        for sd in subdirs:
            subdir_path = dir_path / sd
            landing = _find_landing(subdir_path)
            if landing:
                landing_stem = 'index' if landing[0] == 'index' else 'README'
            else:
                landing_stem = 'index'
            required.append(f"{sd}/{landing_stem}")

        landing = _find_landing(dir_path)
        if landing is None:
            # 生成 stub index.md
            _generate_stub_index(dir_path, title, required)
        else:
            landing_type, landing_path = landing
            # 读取已有内容，提取已有 toctree 条目
            with open(landing_path, 'r', encoding='utf-8') as f:
                content = f.read()
            existing_entries = _extract_toctree_entries(content)
            missing = [e for e in required if e not in existing_entries]
            _append_toctree_entries(landing_path, missing)

        # 递归处理子目录
        for sd in subdirs:
            _process_dir(dir_path / sd, sd)

    _process_dir(source_dir, root_title)


def _generate_conf_py(
    out_dir: Path,
    project: str,
    author: str,
    root_doc: str = "index",
    language: str = "zh_CN",
    mermaid_mode: str = "browser",
):
    """生成 conf.py。

    根据 mermaid_mode 生成不同配置：
    - browser: 浏览器端渲染模式，内联 mermaid.js
    - png: mmdc 构建期预渲染为 PNG 图片
    （auto 模式由 CLI 层预先解析为 browser 或 png）
    """
    if mermaid_mode == "png":
        # 解析 mmdc 完整路径，确保 Windows 下 Popen 可找到 .cmd 文件
        mmdc_path = shutil.which("mmdc")
        if mmdc_path:
            # 使用正斜杠避免 shlex.split 将 Windows 反斜杠当作 POSIX 转义符吃掉
            mermaid_cmd_line = f"mermaid_cmd = {mmdc_path.replace(chr(92), '/')!r}"
        else:
            mermaid_cmd_line = "# WARNING: mmdc not found, set mermaid_cmd to the full path to mmdc"

        conf_content = '''\
# Configuration file for the Sphinx documentation builder.

project = {project!r}
author = {author!r}
extensions = ["myst_parser", "sphinxcontrib.mermaid", "sphinx.ext.mathjax"]
root_doc = {root_doc!r}
language = {language!r}
html_theme = "nature"
myst_heading_anchors = 3
myst_fence_as_directive = ["mermaid"]
myst_enable_extensions = ["dollarmath"]

# png 模式：由 sphinxcontrib-mermaid 调用 mmdc 在构建期渲染为 PNG，
# 产物内嵌图片，无需浏览器端 mermaid.js。
mermaid_output_format = "png"
{mermaid_cmd_line}
'''.format(project=project, author=author, root_doc=root_doc, language=language,
           mermaid_cmd_line=mermaid_cmd_line)
    else:
        conf_content = '''\
# Configuration file for the Sphinx documentation builder.

project = {project!r}
author = {author!r}
extensions = ["myst_parser", "sphinxcontrib.mermaid", "sphinx.ext.mathjax"]
root_doc = {root_doc!r}
language = {language!r}
html_theme = "nature"
myst_heading_anchors = 3
myst_fence_as_directive = ["mermaid"]
myst_enable_extensions = ["dollarmath"]

# 使用 sphinxcontrib-mermaid 的 raw 模式（默认），输出 <pre class="mermaid"> 块，
# 由浏览器端 mermaid.js 渲染。不依赖外部 mmdc 工具。
# mermaid_output_format 默认为 "raw"，无需显式设置。

def setup(app):
    """注入内联 mermaid.js 并抑制扩展的 CDN 脚本。"""
    import md2html
    from pathlib import Path

    # 读取包内预置的 mermaid UMD 构建（v10.9.0，生成 window.mermaid 全局变量）
    assets_dir = Path(md2html.__file__).parent / "assets"
    mermaid_js = (assets_dir / "mermaid.min.js").read_text(encoding="utf-8")

    # 抑制 sphinxcontrib-mermaid 的 CDN ESM 脚本注入，
    # 避免离线环境下 import 失败及 unpkg/jsdelivr 引用。
    # 猴子补丁在事件注册之后无效，改用 html-page-context 过滤。
    def _filter_scripts(app, pagename, templatename, context, doctree):
        script_files = context.get("script_files", [])
        filtered = []
        for sf in script_files:
            attrs = getattr(sf, 'attributes', None) or {{}}
            if attrs.get('type') == 'module':
                continue
            fn = getattr(sf, 'filename', '') or ''
            if 'jsdelivr' in fn or 'unpkg' in fn:
                continue
            filtered.append(sf)
        context["script_files"] = filtered

    app.connect("html-page-context", _filter_scripts, priority=600)

    # 注入 mermaid 库（内联，优先级最高，确保最先加载）
    app.add_js_file(None, body=mermaid_js, priority=10)

    # 注入 mermaid 初始化脚本（逐图渲染 + 失败兜底）
    app.add_js_file(None, body=_MERMAID_INIT_JS, priority=20)

    # 写入 mermaid CSS 文件到 _static/ 并注册
    static_dir = Path(app.srcdir) / "_static"
    static_dir.mkdir(parents=True, exist_ok=True)
    css_path = static_dir / "mermaid.css"
    css_path.write_text(_MERMAID_CSS, encoding="utf-8")
    app.add_css_file("mermaid.css", priority=10)

    return {{"version": "0.1.0", "parallel_read_safe": True}}


_MERMAID_INIT_JS = (
    "document.addEventListener('DOMContentLoaded', async function() {{"
    "    if (typeof mermaid === 'undefined') return;"
    "    mermaid.initialize({{startOnLoad: false, theme: 'default', securityLevel: 'loose'}});"
    "    var els = document.querySelectorAll('pre.mermaid, div.mermaid');"
    "    for (var i = 0; i < els.length; i++) {{"
    "        var el = els[i];"
    "        var code = el.textContent;"
    "        var id = 'mmd-' + Math.random().toString(36).slice(2);"
    "        try {{"
    "            var result = await mermaid.render(id, code);"
    "            var div = document.createElement('div');"
    "            div.className = 'mermaid-rendered';"
    "            div.innerHTML = result.svg;"
    "            el.replaceWith(div);"
    "        }} catch (e) {{"
    "            var errEl = document.getElementById('d' + id);"
    "            if (errEl) errEl.remove();"
    "            var pre = document.createElement('pre');"
    "            pre.className = 'mermaid-error';"
    "            pre.textContent = 'Mermaid \\u6e32\\u67d3\\u5931\\u8d25:\\n' + (e && e.message ? e.message : e) + '\\n\\n' + code;"
    "            el.replaceWith(pre);"
    "        }}"
    "    }}"
    "}});"
)

_MERMAID_CSS = (
    "pre.mermaid {{ display: block; width: 100%; }}"
    "pre.mermaid > svg {{ height: 500px; width: 100%; max-width: 100% !important; }}"
    "pre.mermaid-error {{"
    " border: 2px solid #e74c3c;"
    " background: #fdf0ef;"
    " font-family: monospace;"
    " white-space: pre-wrap;"
    " overflow-x: auto;"
    " padding: 1em;"
    " margin: 1em 0;"
    " color: #c0392b;"
    "}}"
)
'''.format(project=project, author=author, root_doc=root_doc, language=language)
    conf_path = out_dir / 'source' / 'conf.py'
    with open(conf_path, 'w', encoding='utf-8') as f:
        f.write(conf_content)


MAKEFILE_CONTENT = '''# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
'''

MAKEBAT_CONTENT = '''@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
'''

def _generate_makefiles(out_dir: Path):
    """生成标准 Sphinx Makefile 和 make.bat。"""
    makefile_path = out_dir / 'Makefile'
    with open(makefile_path, 'w', encoding='utf-8') as f:
        f.write(MAKEFILE_CONTENT)
    makebat_path = out_dir / 'make.bat'
    with open(makebat_path, 'w', encoding='utf-8') as f:
        f.write(MAKEBAT_CONTENT)


def generate(
    input_path: Path,
    output_dir: Path,
    title: str = "",
    author: str = "",
    exclude_patterns: Optional[List[str]] = None,
    is_single_file: bool = False,
    mermaid_mode: str = "browser",
):
    """生成 Sphinx 项目结构。

    Args:
        input_path: 输入 .md 文件或目录
        output_dir: 输出目录
        title: 项目标题
        author: 作者
        exclude_patterns: CLI 额外排除 glob 列表
        is_single_file: 是否为单文件输入
        mermaid_mode: "browser" 或 "png"
    """
    if exclude_patterns is None:
        exclude_patterns = []

    source_dir = output_dir / 'source'
    source_dir.mkdir(parents=True, exist_ok=True)

    # 读取 .cripperignore（仅当输入是目录时）
    cripper_patterns = []
    if input_path.is_dir():
        cripper_patterns = _read_ignore_patterns(input_path)

    all_patterns = cripper_patterns + exclude_patterns

    # 确定项目标题
    if not title:
        if is_single_file:
            title = input_path.stem
        else:
            title = input_path.name

    # 拷贝输入文件
    if is_single_file:
        dest = source_dir / input_path.name
        shutil.copy2(input_path, dest)
        root_doc = input_path.stem
    else:
        _copy_tree(input_path, source_dir, all_patterns)
        root_doc = "index"

    # 生成 toctree（仅目录模式）
    if not is_single_file:
        _generate_toctrees(source_dir, title)
        if (source_dir / 'README.md').is_file() and not (source_dir / 'index.md').is_file():
            root_doc = "README"

    # 生成 conf.py
    _generate_conf_py(output_dir, project=title, author=author, root_doc=root_doc, mermaid_mode=mermaid_mode)

    # 生成 Makefile 和 make.bat
    _generate_makefiles(output_dir)