import json
import os
import pathlib
import shutil
import subprocess
import typing
import uuid
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from hugodynctx import HugoConfig, PostContext


def get_fullname(ty: type[typing.Any] | typing.Callable):
    name = qualname if (qualname := getattr(ty, "__qualname__", None)) else ty.__name__
    return f"{ty.__module__}.{name}"


def merge_dict(a: dict, b: dict, path: list[str] | None = None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dict(a[key], b[key], [*path, str(key)])
            elif a[key] != b[key]:
                raise Exception("Conflict at " + ".".join([*path, str(key)]))
        else:
            a[key] = b[key]
    return a


class TestPostContext:
    @pytest.fixture
    def hugo_config(
        self, mocker: MockerFixture, tmp_path: Path, request: pytest.FixtureRequest
    ):
        param = getattr(request, "param", None)
        config: dict | None = None
        cwd = tmp_path
        if param:
            if not isinstance(param, dict):
                raise TypeError(param)
            config = param.get("config", config)
            cwd = param.get("cwd", cwd)

        default_config = {
            "contentdir": "content",
            "datadir": "data",
            "publishdir": "public",
            "workingdir": str(cwd),
        }
        mock_which = mocker.patch(
            get_fullname(shutil.which), return_value="/mock/path/to/bin/hugo"
        )
        mock_output = mocker.patch(
            get_fullname(subprocess.check_output),
            return_value=json.dumps(merge_dict(default_config, config or {})).encode(),
        )

        # 避免后续路径出错
        old_cwd = os.getcwd()
        os.chdir(cwd)

        hc = HugoConfig()
        for p in {hc.config_dir, hc.content_dir, hc.data_dir}:
            p.mkdir(parents=True, exist_ok=True)

        yield hc

        os.chdir(old_cwd)
        mock_output.assert_called_once()
        mock_which.assert_called_once()

    @pytest.fixture
    def mock_post_context(self, post_path, hugo_config, mocker: MockerFixture):
        mock_isfile = mocker.patch(get_fullname(pathlib.Path.is_file), return_value=True)
        ctx = PostContext(post_path, hugo_config)
        # NOTE: 提前终止mock避免影响后续执行
        mocker.stop(mock_isfile)
        yield ctx
        mock_isfile.assert_called_once()

    @pytest.mark.parametrize(
        "post_path",
        [
            Path(uuid.uuid4().hex).joinpath("fuck.md"),
            Path(uuid.uuid4().hex).joinpath("bb/fuck.md"),
        ],
    )
    def test_init_error_when_post_is_not_found(self, post_path, hugo_config):
        assert not os.path.exists(post_path)
        with pytest.raises(FileNotFoundError):
            PostContext(post_path, hugo_config)

    @pytest.mark.parametrize(
        "post_path",
        [
            pytest.param(
                "c:/mock/post.md",
                marks=pytest.mark.skipif(os.name != "nt", reason="跳过win的绝对路径"),
            ),
            pytest.param(
                "/mock/post.md",
                marks=pytest.mark.skipif(os.name == "nt", reason="跳过非win的绝对路径"),
            ),
            # 使用相对路径
            "fuck/post.md",
            "post.md",
        ],
    )
    def test_init_error_when_post_path_not_relative_to_config_content_dir(
        self, hugo_config: HugoConfig, mocker: MockerFixture, post_path
    ):
        post_path = Path(post_path).absolute()
        mocker.patch(get_fullname(pathlib.Path.is_file), return_value=True)
        with pytest.raises(ValueError) as exc:
            PostContext(post_path, hugo_config)
        assert exc.value.args[0] == post_path

    @pytest.mark.parametrize(
        ("post_path", "expect"),
        [
            ("content/section/a.md", "/content/section/a.md"),
            ("content/section/b/index.md", "/content/section/b/index.md"),
        ],
    )
    def test_post_abs_path(self, mocker: MockerFixture, hugo_config, post_path, expect):
        mocker.patch(get_fullname(pathlib.Path.is_file), return_value=True)
        ctx = PostContext(post_path, hugo_config)
        assert ctx.post_abs_path == str(Path(expect))

    @pytest.mark.parametrize(
        ("post_path", "expect"),
        [
            ("content/posts/fuck/index.md", "public/posts/fuck/index.html"),
            (
                "content/posts/this is a post.md",
                "public/posts/this-is-a-post/index.html",
            ),
            # 连续的空格
            (
                "content/posts/test      asdf     sdf -    sfa b     .md",
                "public/posts/test------asdf-----sdf------sfa-b-----/index.html",
            ),
            (
                "content/posts/IS CAPITAL  大　    小 　　　   a　　  　　写  letters/index.md",  # noqa: E501
                "public/posts/is-capital--大----小----a--写--letters/index.html",
            ),
            (
                "content/posts/this  IS CAPITAL  大　    小 　   a　写  letters  name.md",  # noqa: E501
                "public/posts/this--is-capital--大----小----a-写--letters--name/index.html",
            ),
            (
                "content/posts/2025/02/大　　　空　 　　格.md",
                "public/posts/2025/02/大-空-格/index.html",
            ),
        ],
    )
    def test_html_path(self, mock_post_context: PostContext, expect, mocker):
        expect = Path(expect)
        if not expect.is_absolute():
            expect = mock_post_context.config.root_dir.joinpath(expect)
        mock_isfile = mocker.patch(get_fullname(Path.is_file), return_value=True)
        assert mock_post_context.html_path == expect
        mock_isfile.assert_called_once()

    @pytest.mark.parametrize(
        ("post_path", "files_in_public_dir"),
        [
            ("content/section/post.md", None),
            (
                "content/section/fuck   a post  /index.md",
                ["public/section/a.html", "public/img.jpg"],
            ),
        ],
    )
    def test_html_path_error_when_html_path_not_found(
        self,
        mock_post_context: PostContext,
        files_in_public_dir: list[str | os.PathLike[str]] | None,
        mocker: MockerFixture,
    ):
        files_in_public_dir = files_in_public_dir or []
        mock_rglob = mocker.patch(
            get_fullname(Path.rglob), return_value=iter(files_in_public_dir)
        )
        with pytest.raises(FileNotFoundError) as exc:
            _ = mock_post_context.html_path
        mocker.stop(mock_rglob)

        mock_rglob.assert_called_once()
        assert isinstance(exc.value.filename, Path)
        assert exc.value.filename.is_relative_to(mock_post_context.config.public_dir)
        assert isinstance(exc.value.filename2, Path)
        assert exc.value.filename2 == mock_post_context.post_path
