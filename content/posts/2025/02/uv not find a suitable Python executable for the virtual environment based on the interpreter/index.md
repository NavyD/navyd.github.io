---
date: 2025-02-08T11:03:25+08:00
draft: false
tags:
  - python
  - venv
---

# UV: Could not find a suitable Python executable for the virtual environment based on the interpreter

在使用mise更新python版本后出现错误，即使重建venv也无效

```powershell
$ uv add --dev types-beautifulsoup4 types-PyYAML
Resolved 23 packages in 45ms
  × Failed to build `hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io`
  ├─▶ Failed to create temporary virtualenv
  ╰─▶ Could not find a suitable Python executable for the virtual environment based on the interpreter: C:\Users\navyd\AppData\Local\mise\installs\python\3.13.1\python.exe
$ rm -Recurse -Force .\.venv
# mise 自动创建venv
$ uv sync
Resolved 20 packages in 1ms
  × Failed to build `hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io`
  ├─▶ Failed to create temporary virtualenv
  ╰─▶ Could not find a suitable Python executable for the virtual environment based on the interpreter: C:\Users\navyd\AppData\Local\mise\installs\python\3.13.1\python.exe
```

## 分析

```console
$ uv --version
uv 0.5.29 (ca73c4754 2025-02-05)
```

尝试移除mise环境，并使用scoop安装uv后发现仍然出现同样的问题。也尝试去检查uv相关源码[crates/uv-virtualenv/src/virtualenv.rs](https://github.com/astral-sh/uv/blob/main/crates/uv-virtualenv/src/virtualenv.rs)，但debug检查数据过于麻烦，也就仅此而已。

```powershell
$ uv python list
cpython-3.14.0a4+freethreaded-windows-x86_64-none    <download available>
cpython-3.14.0a4-windows-x86_64-none                 <download available>
cpython-3.13.2+freethreaded-windows-x86_64-none      <download available>
cpython-3.13.2-windows-x86_64-none                   C:\Users\navyd\AppData\Local\mise\installs\python\3.13.2\python.exe
cpython-3.13.2-windows-x86_64-none                   <download available>
cpython-3.12.9-windows-x86_64-none                   <download available>
cpython-3.12.8-windows-x86_64-none                   C:\Users\navyd\AppData\Local\Programs\Python\Python312\python.exe
cpython-3.11.11-windows-x86_64-none                  C:\Users\navyd\AppData\Roaming\uv\python\cpython-3.11.11-windows-x86_64-none\python.exe
cpython-3.10.16-windows-x86_64-none                  <download available>
cpython-3.9.21-windows-x86_64-none                   <download available>
cpython-3.8.20-windows-x86_64-none                   <download available>
cpython-3.7.9-windows-x86_64-none                    <download available>
pypy-3.10.14-windows-x86_64-none                     <download available>
pypy-3.9.19-windows-x86_64-none                      <download available>
pypy-3.8.16-windows-x86_64-none                      <download available>
pypy-3.7.13-windows-x86_64-none                      <download available

$ $env:UV_PYTHON="$(pwd)\.venv\Scripts\python.exe"
$ $env:UV_PYTHON
C:\Users\navyd\workspaces\projects\navyd.github.io\.venv\Scripts\python.exe
$ uv sync
Resolved 20 packages in 2ms
  × Failed to build `hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io`
  ├─▶ Failed to create temporary virtualenv
  ╰─▶ Could not find a suitable Python executable for the virtual environment based on the interpreter: C:\Users\navyd\AppData\Local\mise\installs\python\3.13.1\python.exe
```

突然发现可能是uv本地数据缓存（非pip包缓存），参考[Cache directory](https://docs.astral.sh/uv/concepts/cache/#cache-directory)移除`%LOCALAPPDATA%\uv\cache`后正常工作

```console
$ mv C:\Users\navyd\AppData\Local\uv C:\Users\navyd\AppData\Local\uv.bak
$ uv sync -vvv
# ...
   Building hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io
       uv_distribution::source::build_distribution dist=hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io
          0.410671s   0ms DEBUG uv_distribution::source Building: hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io
         uv_dispatch::setup_build version_id="hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io", subdirectory=None
            0.415781s   2ms DEBUG uv_workspace::workspace No workspace root found, using project root
            0.416230s   2ms DEBUG uv_virtualenv::virtualenv Using base executable for virtual environment: C:\Users\navyd\AppData\Local\mise\installs\python\3.13.2\python.exe
            0.416777s   3ms DEBUG uv_virtualenv::virtualenv Ignoring empty directory
            0.436989s  23ms DEBUG uv_build_frontend Resolving build requirements
# ...
$ uv run python -V
Python 3.13.2
```

在缓存目录中未找到mise相关python3.13.1目录，可能是不直接使用文本保存数据

```console
$ rg --hidden --no-ignore '\bmise\b'
cache\builds-v0\.tmpk1tLSb\pyvenv.cfg
1:home = C:\Users\navyd\AppData\Local\mise\installs\python\3.11.10

cache\archive-v0\1ckjgyPNIlVA5hCtvFzua\pyvenv.cfg
1:home = C:\Users\navyd\AppData\Local\mise\installs\python\3.11.10

cache\archive-v0\NF0VHsWdceAOZbGh-rKPD\pyvenv.cfg
1:home = C:\Users\navyd\AppData\Local\mise\installs\python\3.11.10

cache\archive-v0\nOmLVxlGvvmTm1jhx7Noh\pyvenv.cfg
1:home = C:\Users\navyd\AppData\Local\mise\installs\python\3.11.10

cache\archive-v0\QJF7lnIHqd6DhEiWozLU9\pyvenv.cfg
1:home = C:\Users\navyd\AppData\Local\mise\installs\python\3.11.10
```

但在uv/cache目录中是存在venv关联的，有venv相关问题可以先禁用缓存再试试

```console
$ l uv\cache
Mode  Size Date Modified    Name
d----    - 2025-02-08 12:07 ./
d----    - 2024-12-19 15:22 ../
d----    - 2025-02-08 12:07 archive-v0/
d----    - 2025-02-08 12:07 builds-v0/
d----    - 2024-12-19 18:41 environments-v1/
d----    - 2024-12-19 15:22 interpreter-v4/
d----    - 2024-12-29 15:07 sdists-v6/
d----    - 2025-02-07 00:37 sdists-v7/
d----    - 2024-12-19 16:48 simple-v14/
d----    - 2025-01-23 12:26 simple-v15/
d----    - 2025-01-05 00:00 wheels-v3/
-a---    1 2024-12-19 15:22 .gitignore
-a---   43 2024-12-19 15:22 CACHEDIR.TAG
```

注意：*即使可以使用`uv sync --no-cache`正常工作，但后续未指定`--no-cache`时的命令仍然会失败*

```console
$ uv sync --no-cache
Resolved 20 packages in 2ms
      Built hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io
Prepared 1 package in 2.14s
Uninstalled 1 package in 6ms
Installed 1 package in 17ms
 ~ hugodynctx==0.1.0 (from file:///C:/Users/navyd/workspaces/projects/navyd.github.io)

$ uv add --dev types-beautifulsoup4 types-PyYAML -vvv
# ...
   Building hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io
       uv_distribution::source::build_distribution dist=hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io
          0.215427s   0ms DEBUG uv_distribution::source Building: hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io
         uv_dispatch::setup_build version_id="hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io", subdirectory=None
            0.218969s   1ms DEBUG uv_workspace::workspace No workspace root found, using project root
            0.219232s   2ms DEBUG uv_virtualenv::virtualenv Using base executable for virtual environment: C:\Users\navyd\AppData\Local\mise\installs\python\3.13.1\python.exe
            0.219747s   2ms DEBUG uv_virtualenv::virtualenv Ignoring empty directory
        0.224332s  19ms DEBUG uv_fs Released lock at `C:\Users\navyd\AppData\Local\uv\cache\sdists-v7\editable\09b11b31b7612a34\.lock`
        0.224834s  16ms DEBUG uv_fs Released lock at `C:\Users\navyd\AppData\Local\uv\cache\wheels-v3\index\a3dff561ea463217\types-html5lib\types_html5lib-1.1.11.20241018-py3-none-any.lock`
        0.225186s  18ms DEBUG uv_fs Released lock at `C:\Users\navyd\AppData\Local\uv\cache\wheels-v3\index\a3dff561ea463217\types-pyyaml\types_pyyaml-6.0.12.20241230-py3-none-any.lock`
        0.225566s  19ms DEBUG uv_fs Released lock at `C:\Users\navyd\AppData\Local\uv\cache\wheels-v3\index\a3dff561ea463217\types-beautifulsoup4\types_beautifulsoup4-4.12.0.20250204-py3-none-any.lock`
    0.226420s DEBUG uv::commands::project::add Reverting changes to `pyproject.toml`
    0.228047s DEBUG uv::commands::project::add Reverting changes to `uv.lock`
  × Failed to build `hugodynctx @ file:///C:/Users/navyd/workspaces/projects/navyd.github.io`
  ├─▶ Failed to create temporary virtualenv
  ╰─▶ Could not find a suitable Python executable for the virtual environment based on the interpreter: C:\Users\navyd\AppData\Local\mise\installs\python\3.13.1\python.exe

$ uv add --dev types-beautifulsoup4 types-PyYAML
Installed 4 packages in 34ms
 ~ hugodynctx==0.1.0 (from file:///C:/Users/navyd/workspaces/projects/navyd.github.io)
 + types-beautifulsoup4==4.12.0.20250204
 + types-html5lib==1.1.11.20241018
 + types-pyyaml==6.0.12.20241230
```
## 解决

手动删除`%LOCALAPPDATA%\uv\cache`重建venv
