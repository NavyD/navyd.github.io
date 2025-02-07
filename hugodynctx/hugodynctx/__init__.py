import abc
import concurrent
import concurrent.futures
import datetime
import json
import logging
import mimetypes
import multiprocessing
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import typing
import urllib
import urllib.parse
from collections.abc import Sequence
from functools import cached_property
from typing import Annotated

import box
import bs4
import jinja2
import typer
import yaml

LOG = logging.getLogger(__name__)


class HugoBuildError(Exception):
    pass


class FrontMatterParseError(HugoBuildError):
    pass


class HugoHtmlParseError(HugoBuildError):
    pass


class HugoConfig:
    def __init__(
        self,
        environment: str | None = None,
        work_dir: str | os.PathLike[str] = ".",
        binpath: str = "hugo",
    ) -> None:
        self._work_dir = pathlib.Path(work_dir)
        self.log = LOG.getChild(self.__class__.__name__)

        print(f"{self.log.name} {__name__} {self.__class__.__name__}")
        hugo_bin_path = shutil.which(binpath)
        if not hugo_bin_path:
            raise FileNotFoundError(binpath)
        self._binpath = hugo_bin_path
        conf_args = [
            binpath,
            "config",
            "--format",
            "json",
            *(["--environment", environment] if environment else []),
        ]
        self.log.info("Getting hugo config with args: %s", conf_args)
        s = subprocess.check_output(conf_args, cwd=work_dir).decode()
        self._config: dict[str, typing.Any] = json.loads(s)
        self._environment = environment
        self._work_dir = pathlib.Path(work_dir)

    @property
    def environment(self) -> str | None:
        return self._environment

    @cached_property
    def data(self) -> box.Box:
        return box.Box(self._config, default_box=True)

    @property
    def binpath(self) -> str:
        return self._binpath

    @property
    def workingdir(self) -> pathlib.Path:
        # return pathlib.Path(self._config["workingdir"])
        # NOTE: workingdir是绝对路径，可能会于work_dir不一致
        return self._work_dir

    @property
    def data_dir(self) -> pathlib.Path:
        return self.workingdir.joinpath(self._config["datadir"])

    @property
    def public_dir(self) -> pathlib.Path:
        return self.workingdir.joinpath(self._config["publishdir"])

    @property
    def content_dir(self) -> pathlib.Path:
        return self.workingdir.joinpath(self._config["contentdir"])

    @property
    def config_dir(self) -> pathlib.Path:
        return self.workingdir.joinpath("config")

    def get_section_dir(self, section: str | os.PathLike[str]) -> pathlib.Path:
        return self.content_dir.joinpath(section)


class ContentAdapterPageDates(typing.TypedDict, total=False):
    date: str | None
    expiryDate: str | None
    lastmod: str | None
    publishDate: str | None


class ContentAdapterPageContent(typing.TypedDict, total=False):
    mediaType: str | None
    value: str | None


class ContentAdapterPage(typing.TypedDict, total=False):
    path: typing.Required[str]
    title: typing.Required[str]
    summary: str | None
    params: dict[str, typing.Any]
    dates: ContentAdapterPageDates


class ContentAdapter(typing.TypedDict):
    page: ContentAdapterPage
    section: str


class DynContentDict(typing.TypedDict):
    src_contents: dict[str, ContentAdapter]
    config: dict[str, typing.Any]


class DateLoader(yaml.SafeLoader):
    pass


def front_matter_date_constructor(
    loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode
) -> str:
    return loader.construct_scalar(node)


# 解析yaml中的date格式从默认的datetime为str类型，
# 避免front_matter.date作为datetime还要再次format出错
# [Can PyYAML parse iso8601 dates?](https://stackoverflow.com/a/13295663/8566831)
DateLoader.add_constructor("tag:yaml.org,2002:timestamp", front_matter_date_constructor)


class GenerateContext(abc.ABC):
    def __init__(self, post_path: str | os.PathLike[str], config: HugoConfig) -> None:
        self.post_path = pathlib.Path(post_path)
        self.config = config
        self.log = LOG.getChild(self.__class__.__name__)

    @cached_property
    def html_path(self) -> pathlib.Path:
        rel_section_path = self.post_path.relative_to(self.config.content_dir)
        if rel_section_path.name == "index.md":
            rel_section_html_path = rel_section_path.with_suffix(".html")
        else:
            rel_section_html_path = rel_section_path.with_suffix("").joinpath(
                "index.html"
            )
        return self.config.public_dir.joinpath(rel_section_html_path)

    @cached_property
    def front_matter(self) -> box.Box:
        data = self.parse_front_matter(self.post_path) or {}
        return box.Box(data, default_box=True)

    @cached_property
    def section(self) -> str:
        return self.post_path.relative_to(self.config.content_dir).parts[0]

    def parse_front_matter(
        self,
        post_path: str | os.PathLike[str],
        front_matter_sep_start: str = "---",
        front_matter_sep_end: str = "---",
    ) -> dict[str, object] | None:
        self.log.debug("Parsing front matter for file %s", post_path)
        with open(post_path) as post_file:
            first_line = post_file.readline().rstrip()
            self.log.debug(
                "Got first line %s for front matter file %s", first_line, post_path
            )
            if not first_line.startswith(front_matter_sep_start):
                return None

            if first_line == front_matter_sep_start:
                front_matter_text = ""
                while True:
                    line = post_file.readline()
                    if not line:
                        self.log.error(
                            "Not found end of front matter %s for file %s",
                            front_matter_sep_end,
                            post_path,
                        )
                        raise FrontMatterParseError(post_path)
                    if line.rstrip() == front_matter_sep_end:
                        break
                    front_matter_text = f"{front_matter_text}{line}"
                self.log.debug("Loading yaml front matter data")
                # NOTE: 使用定制的date解析为str避免默认的datetime导致需要格式化
                return yaml.load(front_matter_text, Loader=DateLoader)  # noqa: S506

            self.log.error(
                "Unsupported front matter %s for file %s", first_line, post_path
            )
            raise FrontMatterParseError(first_line, post_path)

    def generate(self) -> tuple[str, ContentAdapter]:
        self.log.debug("Generating context for post %s", self.post_path)
        with open(self.html_path) as hf:
            doc = bs4.BeautifulSoup(hf, "lxml")

        # 获取title 默认使用front_matter
        title = self.front_matter.title
        # 获取h1/h2内容作为title
        if not title and (head_doc := doc.select_one("body h1[id],body h2[id]")):
            title = head_doc.text.strip()
        # 默认使用文件名作为title
        if not title:
            title = (
                self.html_path.parent.name.replace("-", " ").replace("_", " ").title()
            )

        # 当前页面的url相对section的路径
        logical_path = self.html_path.parent.relative_to(
            self.config.public_dir.joinpath(self.section)
        )
        page = ContentAdapterPage(path=str(logical_path), title=title)

        self._update_page(page, doc)

        # 当前post相对于hugo项目根目录的绝对路径，用于gotmpl中的`os.ReadFile`读取使用
        post_abs_path = urllib.parse.urljoin("/", str(self.post_path))
        # TODO: 在new-section模式中添加Resource map避免无法加载img
        return post_abs_path, ContentAdapter(page=page, section=self.section)

    @abc.abstractmethod
    def _update_page(self, page: ContentAdapterPage, doc: bs4.BeautifulSoup) -> None: ...

    @classmethod
    def gen_environment(
        cls, config_dir: str | os.PathLike[str], name: str | None = None
    ) -> pathlib.Path | None:
        return None


class GenerateContext4StackTheme(GenerateContext):
    def _update_page(self, page: ContentAdapterPage, doc: bs4.BeautifulSoup) -> None:
        article_doc = doc.select_one("main article.main-article")
        if not article_doc:
            raise HugoHtmlParseError

        # 配置日期
        dates = ContentAdapterPageDates()
        dates["date"] = self.front_matter.date or None
        dates["expiryDate"] = (
            self.front_matter.expiryDate or self.front_matter.unpublishdate or None
        )
        dates["publishDate"] = (
            # alias
            self.front_matter.publishDate
            or self.front_matter.published
            or self.front_matter.pubdate
            or (
                published_doc.text.strip()
                if (published_doc := article_doc.select_one(".article-time--published"))
                else None
            )
        )
        dates["lastmod"] = (
            self.front_matter.lastmod
            or self.front_matter.modified
            or (
                lastmod_doc.text.strip()
                .replace("Last updated on", "")
                # .replace("最后更新于", "")
                .strip()
                if (lastmod_doc := article_doc.select_one(".article-lastmod span"))
                else None
            )
            # 没有lastmod时使用文件修改时间
            or (
                datetime.datetime.fromtimestamp(
                    self.post_path.stat().st_mtime, tz=datetime.UTC
                ).isoformat()
            )
        )
        page["dates"] = dates

        params = page.setdefault("params", {})

        # 添加文章简介
        content_doc = article_doc.select_one("section.article-content")
        if not content_doc:
            raise HugoHtmlParseError
        summary = ""
        head_doc = content_doc.select_one("h1[id],h2[id]")
        if head_doc:
            # 取head前的内容
            for sib in reversed(list(head_doc.previous_siblings)):
                summary += sib.text
            summary = summary.strip()
            if isinstance(summ_len := self.config.data.summarylength, int):
                if not summary:
                    summary = head_doc.text.strip()
                    if summary == page.get("title", "").strip():
                        # 如果h1/h2前无内容且与title一样，则移除h1本身避免重复
                        summary = ""
                    # 取head后内容直到满足len
                    for sib in head_doc.next_siblings:
                        if len(summary) >= summ_len:
                            break
                        summary += sib.text
                    summary = summary.rstrip()
                padding = "..."
                # 截取超出长度的部分
                if (summ_pad_len := summ_len - len(padding)) > 0 and summ_len < len(
                    summary
                ):
                    summary = f"{summary[:summ_pad_len]}{padding}"
        else:
            summary = None
        params["description"] = summary

        # 获取第1个image作为cover
        cover = None
        post_dir = self.post_path.parent
        for path in post_dir.glob("*"):
            ty, _ = mimetypes.guess_type(path)
            if ty and ty.startswith("image"):
                cover = path.relative_to(post_dir)
                cover = str(cover)
                break
        # 不存在本地image时获取首个img元素链接作为cover
        if not cover and (img_doc := article_doc.select_one("img[src][loading]")):
            cover = img_doc.attrs["src"]
        params["image"] = cover

        # 获取tags
        params["tags"] = self.front_matter.tags or self.front_matter.params.tags or None

    @classmethod
    def gen_environment(
        cls, config_dir: str | os.PathLike[str], name: str | None = None
    ) -> pathlib.Path | None:
        if not name:
            name = f".{__name__}"
        env_path = pathlib.Path(config_dir).joinpath(name)
        # if env_path.exists():
        #     raise FileExistsError(env_path)
        env_path.mkdir(parents=True, exist_ok=True)

        gen_gitignore(env_path)

        conf_path = env_path.joinpath("hugo.json")
        conf_data = {
            # 设置en避免date被出现中英文翻译的问题
            "defaultContentLanguage": "en",
            "languages": {
                "en": {
                    "languageName": "English",
                }
            },
            "Params": {
                # NOTE: 必须使用iso格式解析否则time.AsTime解析不了
                # 参考
                # * [time.AsTime](https://gohugo.io/functions/time/astime/)
                # * [time#pkg-constants](https://pkg.go.dev/time#pkg-constants)
                "DateFormat": {
                    "published": "2006-01-02T15:04:05Z07:00",
                    "lastUpdated": "2006-01-02T15:04:05Z07:00",
                }
            },
        }
        LOG.debug("Creating temp hugo config file %s: %s", conf_path, conf_data)
        with open(conf_path, "w+") as f:
            json_dump(conf_data, f)
        return env_path


def gen_gitignore(
    gitignore_dir: str | os.PathLike[str], rules: str | Sequence[str] = "*"
) -> None:
    if isinstance(rules, str):
        rules = (rules,)
    gitignore_path = pathlib.Path(gitignore_dir).joinpath(".gitignore")
    LOG.debug("Generating gitignore file %s with rules: %s", gitignore_path, rules)
    with open(gitignore_path, "w+") as f:
        f.write("\n".join(rules))


def gen_data(ctx: GenerateContext) -> tuple[str, ContentAdapter]:
    return ctx.generate()


class ContentBuilder:
    def __init__(
        self,
        hugo_conf: HugoConfig,
        section_post_globs: typing.Mapping[str, Sequence[str]],
        context: type[GenerateContext],
        new_section: str | None = None,
    ) -> None:
        self.log = LOG.getChild(self.__class__.__name__)
        self._hugo_conf = hugo_conf
        self._executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        )
        self._tempdir = tempfile.TemporaryDirectory(suffix=f".hugo-{__name__}")
        self._new_section = new_section
        self._ctx_gotmpl_name = "_content.gotmpl"
        self.log.debug(
            "Checking if section globs %s exists in %s",
            section_post_globs,
            hugo_conf.content_dir,
        )
        for section in section_post_globs:
            if not (sect_dir := hugo_conf.get_section_dir(section)).is_dir():
                raise NotADirectoryError(sect_dir)

        if new_section and (
            (
                sect_paths := (sect_dir := hugo_conf.get_section_dir(new_section))
            ).is_file()
            or (
                sect_dir.is_dir()
                and (sect_paths := set(sect_dir.glob("*")))
                != {".gitignore", self._ctx_gotmpl_name}
            )
        ):
            raise FileExistsError(sect_dir, sect_paths)

        self._context = context

        # [How to load jinja template directly from filesystem](https://stackoverflow.com/a/38642558/8566831)
        self._jinjia_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(pathlib.Path(__file__).parent),
            autoescape=jinja2.select_autoescape(),
        )
        self._section_post_globs = section_post_globs

    def build_hugo(self, environment: str | None = None) -> None:
        args = [
            self._hugo_conf.binpath,
            "build",
            "--buildDrafts",
            "--buildExpired",
            *(("--environment", environment) if environment else ()),
        ]
        self.log.info("Build hugo with args: %s", args)
        # [Redirect subprocess stderr to stdout](https://stackoverflow.com/a/11495784/8566831)
        subprocess.check_call(args, stdout=sys.stderr.buffer)

    def gen_content(self, section: str, post_globs: Sequence[str]) -> DynContentDict:
        section_dir = self._hugo_conf.content_dir.joinpath(section)
        self.log.debug(
            "Getting post paths with globs %s in directory %s",
            post_globs,
            section_dir,
        )
        post_paths = {
            p
            for glob in post_globs
            for p in section_dir.glob(glob)
            if p.name != "_index.md"
        }
        self.log.debug("Got %s post paths: %s", len(post_paths), post_paths)

        # NOTE:
        # 不能包含类中的self作为参数[TypeError: can't pickle _thread.lock objects](https://stackoverflow.com/a/50409663/8566831)
        # 不能使用闭包作为多进程[AttributeError: Can't pickle local object in Multiprocessing](https://stackoverflow.com/a/72776044/8566831)
        tasks = [
            self._executor.submit(gen_data, self._context(p, self._hugo_conf))
            for p in post_paths
        ]
        src_contents = {}
        for fut in concurrent.futures.as_completed(tasks):
            try:
                src, ctn = fut.result()
            except Exception:
                raise
            else:
                src_contents[src] = ctn
        return DynContentDict(src_contents=src_contents, config=self._hugo_conf.data)

    def build(self) -> None:
        env_path = self._context.gen_environment(self._hugo_conf.config_dir)
        self.build_hugo(environment=env_path.name if env_path else None)
        if self._new_section:
            dyn_data = DynContentDict(src_contents={}, config=self._hugo_conf.data)
            for section, globs in self._section_post_globs.items():
                data = self.gen_content(section, globs)
                dyn_data["src_contents"] |= data["src_contents"]
            section_dir = self._hugo_conf.get_section_dir(self._new_section)
            section_dir.mkdir(parents=True, exist_ok=True)
            self.gen_dyn_section(section_dir)
            self.gen_dyn_data(dyn_data, self._new_section)
        else:
            for section, globs in self._section_post_globs.items():
                data = self.gen_content(section, globs)
                section_dir = self._hugo_conf.get_section_dir(section)
                self.gen_dyn_section(section_dir)
                self.gen_dyn_data(data, section)
        self.build_hugo()

    def gen_dyn_section(self, section_dir: pathlib.Path) -> None:
        if not section_dir.exists():
            raise FileNotFoundError(section_dir)

        jinja_hugo_dict = {"section": section_dir.name}
        jinja_dict = {"hugo": jinja_hugo_dict}
        jinja_gotmpl_name = f"{self._ctx_gotmpl_name}.jinja"

        self.log.debug(
            "Rendering %s template with data: %s", jinja_gotmpl_name, jinja_dict
        )
        dyn_ctx_gotmpl_str = self._jinjia_env.get_template(jinja_gotmpl_name).render(
            **jinja_dict
        )

        ctn_gotmpl_path = section_dir.joinpath(self._ctx_gotmpl_name)
        self.log.debug(
            "Writing %s length to %s", len(dyn_ctx_gotmpl_str), ctn_gotmpl_path
        )
        with open(ctn_gotmpl_path, "w+") as f:
            f.write(dyn_ctx_gotmpl_str)

        gen_gitignore(section_dir, rules=(".gitignore", self._ctx_gotmpl_name))

    def gen_dyn_data(self, data: object, section: str) -> None:
        """生成`data/$section/$section.json`用于gotmpl中使用的数据"""
        dyn_data_dir = self._hugo_conf.data_dir.joinpath(section)
        dyn_data_path = dyn_data_dir.joinpath(f"{section}.json")
        dyn_data_dir.mkdir(parents=True, exist_ok=True)

        self.log.debug("Generating dyn data to %s", dyn_data_path)
        with open(dyn_data_path, "w+") as f:
            json_dump(data, f)

        gen_gitignore(dyn_data_dir, rules=(".gitignore", dyn_data_path.name))


@typing.overload
def json_dump(data: object, file: typing.IO) -> None: ...
@typing.overload
def json_dump(data: object) -> str: ...
def json_dump(data: object, file: typing.IO | None = None) -> str | None:
    # NOTE: [Make the Python json encoder support Python's new dataclasses](https://stackoverflow.com/a/51286749/8566831)
    # NOTE: [Saving UTF-8 texts with json.dumps as UTF-8, not as a \u escape sequence](https://stackoverflow.com/a/18337754/8566831)
    opt = {"ensure_ascii": False, "indent": 2}
    if file:
        json.dump(data, file, **opt)
        return None
    return json.dumps(data, **opt)


app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


# NOTE: [Is support for Union types on the roadmap? #461](https://github.com/fastapi/typer/issues/461)
@app.command(help=("通过hugo构建本地post动态生成主题相关的静态网站"))
def cli(
    section_globs: Annotated[
        list[pathlib.Path],
        typer.Argument(
            help=(
                "指定section下需要构建的post的glob。如`section/**/*.md`"
                "如果仅指定section则使用section_default_globs"
            ),
        ),
    ],
    new_section: Annotated[
        str | None,
        typer.Option(
            "--new-section",
            "-n",
            help="生成相关构建数据到新的section中。否则将生成的数据放入当前指定的sections",
        ),
    ] = None,
    # NOTE: hugo所有相对目录基于当前目录
    work_dir: pathlib.Path = pathlib.Path("."),
    section_default_globs: list[str] = ["**/*.md"],  # noqa: B006
    config_environment: Annotated[
        str | None, typer.Option("--config-environment", "-e")
    ] = None,
    hugo_bin: pathlib.Path = pathlib.Path("hugo"),
    verbose: Annotated[
        int, typer.Option("--verbose", "-v", count=True, min=0, max=2)
    ] = 0,
    # temp_environment: Annotated[str | None, typer.Option()] = None,
    # TODO: 支持`--command -- hugo build --environment production`
    # command: Annotated[list[str] | None, typer.Option(allow_dash=True)] = None,
) -> None:
    section_post_globs: dict[str, list[str]] = {}
    for p in section_globs:
        parts = p.parts
        if len(parts) < 1:
            raise ValueError(p)
        section = parts[0]
        globs = parts[1:] if len(parts) > 1 else section_default_globs
        section_post_globs.setdefault(section, []).extend(globs)

    logging.basicConfig(
        format=(
            "%(asctime)s.%(msecs)03d [%(levelname)-5s] [%(name)s.%(funcName)s]: "
            "%(message)s"
        ),
        level=logging.ERROR,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log_levels = (logging.ERROR, logging.INFO, logging.DEBUG)
    LOG.setLevel(log_levels[verbose])

    if work_dir:
        os.chdir(work_dir)
    hugo_config = HugoConfig(
        environment=config_environment, work_dir=work_dir, binpath=str(hugo_bin)
    )
    ContentBuilder(
        hugo_config,
        section_post_globs=section_post_globs,
        new_section=new_section,
        context=GenerateContext4StackTheme,
    ).build()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
