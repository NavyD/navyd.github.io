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
    def hugo_config(self, mocker: MockerFixture, tmp_path):
        mock_which = mocker.patch(
            get_fullname(shutil.which), return_value="/mock/path/to/bin/hugo"
        )
        mock_output = mocker.patch(
            get_fullname(subprocess.check_output),
            return_value=json.dumps(
                {
                    "contentdir": "content",
                    "datadir": "data",
                    "publishdir": "public",
                }
            ).encode(),
        )
        # 避免后续路径出错
        old_cwd = os.getcwd()
        os.chdir(tmp_path)

        yield HugoConfig(work_dir=tmp_path)

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

    def test_init_error_when_cwd_is_not_config_root_dir(
        self, hugo_config: HugoConfig, tmp_path: Path, mocker: MockerFixture
    ):
        # assert tmp_path != Path.cwd()
        # NOTE: tmp_path与fixture时的tmp_path一样可能导致未改变cwd
        new_cwd = tmp_path.joinpath(uuid.uuid4().hex[:8])
        new_cwd.mkdir(parents=True)
        os.chdir(new_cwd)

        rel_post_path = hugo_config.content_dir.relative_to(
            hugo_config.root_dir
        ).joinpath("posts/fuck.md")
        mocker.patch(get_fullname(pathlib.Path.is_file), return_value=True)
        with pytest.raises(ValueError) as exc:
            PostContext(rel_post_path, hugo_config)
        assert exc.value.args[0] == rel_post_path
        assert exc.value.args[1] == new_cwd
        assert exc.value.args[2] == hugo_config.root_dir

    def test_init_error_when_post_path_not_relative_to_config_content_dir(
        self, tmp_path: Path, hugo_config: HugoConfig, mocker: MockerFixture
    ):
        abs_post_path = tmp_path.joinpath(uuid.uuid4().hex[:8]).joinpath("fuck post.md")
        mocker.patch(get_fullname(pathlib.Path.is_file), return_value=True)
        with pytest.raises(ValueError) as exc:
            PostContext(abs_post_path, hugo_config)
        assert exc.value.args[0] == abs_post_path

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
            (
                "content/posts/test      asdf     sdf -    sfa b     .md",
                "public/posts/test------asdf-----sdf------sfa-b-----/index.html",
            ),
        ],
    )
    def test_html_path(self, mock_post_context: PostContext, expect):
        expect = Path(expect)
        if not expect.is_absolute():
            expect = mock_post_context.config.root_dir.joinpath(expect)
        assert mock_post_context.html_path == expect
