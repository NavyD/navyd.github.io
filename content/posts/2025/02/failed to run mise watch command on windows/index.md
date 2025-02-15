---
title: Failed to Run Mise Watch Command on Windows
date: 2025-02-15T16:11:25+08:00
draft: false
tags: [rust, windows, DevOps]
---

在使用 [mise](https://github.com/jdx/mise) 运行监控任务`mise watch build`时出错：

```console
$ mise watch build
[Running: mise run build]
The application panicked (crashed).
Message:  called `Option::unwrap()` on a `None` value
Location: C:\Users\navyd\.cargo\registry\src\rsproxy.cn-0dccff568467c15b\xx-2.0.4\src\file.rs:222

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
The application panicked (crashed).
Message:  called `Option::unwrap()` on a `None` value
Location: C:\Users\navyd\.cargo\registry\src\rsproxy.cn-0dccff568467c15b\xx-2.0.4\src\file.rs:222

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
The application panicked (crashed).
Message:  called `Option::unwrap()` on a `None` value
Location: C:\Users\navyd\.cargo\registry\src\rsproxy.cn-0dccff568467c15b\xx-2.0.4\src\file.rs:222

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
[Waiting 10s for processes to exit before stopping...]
```

## 分析

下面是一些简单的配置信息

```toml
[env]
_.python.venv = { path = ".venv", create = true }
_.file = ".env"
[settings]
windows_default_inline_shell_args = "powershell -NoProfile -NonInteractive -Command"
[tasks.build]
run_windows = '''
&{ echo first; echo second; }
'''
sources = ["content/posts/**/*.md"]
outputs = ["data/posts/posts.json"]
```

```console
$ mise -V
2025.2.3 windows-x64 (2025-02-09)
$ watchexec -V
watchexec 2.1.2
```

我在 [xx::file::glob](https://github.com/jdx/xx/blob/5a43124c6f39246ada155d6b46edd3aec787ddcf/src/file.rs#L221) 中找到

```rust
    let root = input
        .ancestors()
        .skip(1)
        .find(|a| !"*[{?".chars().any(|c| a.to_str().unwrap().contains(c)))
        .unwrap()
        .to_path_buf();
```

发现是由于`input`路径中的最顶级路径中存在任意的`*[{?`字符导致的 unwrap 异常，如 `\\\\?\\C:\\Users\\xxxx` 。

```rust
assert_eq!(
    std::path::Path::new("\\\\?\\C:\\Users\\xxxx")
        .ancestors()
        .skip(1)
        .find(|a| !"*[{?".chars().any(|c| a.to_str().unwrap().contains(c))),
    None
);
```

这里吐槽一句，但凡将`Option::ok()`转为 `Result::Err` 返回错误或使用 `Option::unwrap_or_else` 处理错误信息，也不至于浪费许多时间检查问题所在！害得我在源码中打 debug 日志查看是什么 `input` 导致的问题。

在 mise 源码中只能使用 debug 日志输出大法，没法用 debug 调试，首先当前的 rust debug 体验极差，只有少数基础类型有能被可视化，一个变量稍微包装一下如 `AsRef<Path>` 这种类型都无法直观查看值，只有指针地址...，更别说使用对静态语言在 watch 调用类型函数这种是不可能的（静态分发编译完成后不必要的函数不会被编译，且还有 inline 这种存在），还是 python 好！另外，对于 `mise watch build` 这种 mise 调用 `watchexec -- mise run build` 再被 watchexec 调用 `mise run build` 调用链比较复杂，debug 体验可能不会好，但应该能正常使用，应该，没试过。。。

通过日志输出 [mise log](mise%20watch%20build%20--log-level%20trace%20--%20--log-level%20trace.log) 中有

```log
DEBUG  1 [src\config\mod.rs:106] Loaded config paths ["\\\\?\\C:\\Users\\navyd\\workspaces\\projects\\navyd.github.io\\mise.toml", "\\\\?\\C:\\Users\\navyd\\.config\\mise\\config.toml"] from config filenames: [".bun-version", ".deno-version", ".go-version", ".java-version", ".node-version", ".nvmrc", ".python-version", ".python-versions", ".ruby-version", ".sdkmanrc", ".swift-version", ".terraform-version", ".zig-version", "Gemfile", "rust-toolchain.toml", ".tool-versions", ".config/mise/conf.d/*.toml", ".config/mise/config.toml", ".config/mise.toml", ".mise/config.toml", "mise/config.toml", ".rtx.toml", "mise.toml", ".mise.toml", ".config/mise/config.local.toml", ".config/mise.local.toml", ".mise/config.local.toml", ".rtx.local.toml", "mise.local.toml", ".mise.local.toml"]
```

发现是 [mise::dir::CWD](https://github.com/jdx/mise/blob/0a1b4f58e3a975be40f9bc37299b517972830ae3/src/dirs.rs#L8) 使用 [std::env::current_dir](https://doc.rust-lang.org/std/env/fn.current_dir.html) 返回了 `\\\\?\\C:\\Users\\xxxx` 导致后续的异常，根据文档指出在 windows 上使用 [GetCurrentDirectory function (winbase.h)](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getcurrentdirectory) ，虽然其中有提到 `\\servername\sharename` 存在这样的形式目录，但我从未见过，且与 `\\\\?\\C:\\Users\\xxxx` 不怎么像就未在意，错失先机！

我怀疑可能是 mise 的问题，尝试在 mise 源码目录中参考 [cargo Package Layout](https://doc.rust-lang.org/cargo/guide/project-layout.html) 添加一个 bin 可执行命令 `src\bin\printenv.rs`，用于打印 cwd 和环境变量

```rust
fn main() {
    println!("current env dir: {:?}", std::env::current_dir());
    let envs = std::env::vars()
        .map(|(k, v)| format!("{k}={v}"))
        .collect::<Vec<_>>()
        .join("\n");
    println!("all env: \n{envs}")
}
```

然后修改部分代码让 `mise watch build` 实际改为 `watchexec -- target/debug/printenv.exe` 运行，查看 [printenv.log](mise%20watch%20build%20printenv.log) 结果发现 `current_dir()` 依然是 `\\\\?\\C:\\Users\\navyd\\workspaces\\projects\\mise`。

尝试改为运行 python 中的 `os.getcwd()` 试试

```rust
let args = vec!["python", "-c", r#"'import os; print(os.getcwd()); import subprocess; subprocess.check_call(["""C:/Users/navyd/workspaces/projects/mise/target/debug/printenv.exe"""], env={})'"#];
```

```console
$ .\target\debug\mise.exe watch build
[Running: python -c 'import os; print(os.getcwd()); import subprocess; subprocess.check_call(["""C:/Users/navyd/workspaces/projects/mise/target/debug/printenv.exe"""], env={})']
mise WARN  missing: bun@1.2.2 cargo:cargo-edit@0.13.1 cargo:cargo-insta@1.42.1 cargo:git-cliff@2.8.0 npm:markdownlint-cli@0.44.0
\\?\C:\Users\navyd\workspaces\projects\mise
current env dir: Ok("\\\\?\\C:\\Users\\navyd\\workspaces\\projects\\mise")
all env:
```

结果依然是 `\\\\?\\C:\\Users\\navyd\\workspaces\\projects\\mise` ，即使我尝试清空所有环境变量运行 printenv 也没用！

### deepseek

我尝试询问 deepseek 有什么建议：

#### Human

在 windows 上使用 powershell 运行下面的 python 命令 `python -c 'import os; print(os.getcwd())'` ，其输出为 `\\?\C:\Users\usernamexxx\workspaces`，为什么会出现 `\\?\` 前缀字符，而不是 `C:\Users\usernamexxx\workspaces` 呢？

#### Assistant

<details>
    <summary>Thinking Process (35s):</summary>
嗯，用户问在 Windows 的 PowerShell 里运行那个 Python 命令，结果输出有\\?\前缀，而不是直接显示路径。这个问题我需要仔细想想。首先，得回忆一下 Windows 的路径处理机制。

我记得在 Windows 中，普通的路径长度是有限制的，通常是 260 个字符左右。而如果路径前面加上\\?\的话，应该是启用了扩展长度路径，可以支持更长的路径。这种情况下，Python 可能返回的是这种扩展格式的路径，所以才会出现那个前缀。

那用户的情况里，为什么会触发这个呢？可能用户当前的工作目录路径本身比较长，或者 Python 在某些情况下自动使用扩展路径。例如，当 Python 检测到路径可能超过限制时，或者当在 PowerShell 中某些配置导致工作目录以扩展形式返回。

接下来，我需要确认一下 os.getcwd() 在 Windows 下的行为。查阅 Python 文档的话，可能会发现当路径超过 260 字符时，或者使用某些 API 获取路径时，可能会返回带有\\?\的 UNC 路径形式。这可能是因为 Python 内部使用了 GetFinalPathNameByHandle 或类似的函数，返回了这种格式的路径。

另外，PowerShell 的环境可能和普通的 cmd 不同。比如，PowerShell 可能默认启用了某些长路径支持，或者执行策略导致 Python 以不同的方式处理路径。也有可能用户的工作目录本身是通过某种方式创建的，比如符号链接或 Junction 点，导致路径被解析为扩展形式。

或者，用户可能在使用 Python 时以某种方式激活了长路径支持，比如在注册表中启用了长路径，或者 Python 脚本本身调用了 API 来允许长路径，导致返回的路径带有这个前缀。

那解决方案的话，可能需要告诉用户如何避免这种情况。例如，使用 os.path.abspath('.') 代替 os.getcwd()，因为前者可能不会返回扩展路径。或者，检查 Python 的版本，某些版本的 Python 可能在处理路径时有不同的行为。另外，用户如果想去除这个前缀，可以在获取路径后进行处理，替换掉\\?\部分。

不过，我需要验证这些猜测。比如，在 Python 中，当调用 os.getcwd() 时，是否在某些情况下返回扩展路径。比如，如果当前目录是使用扩展路径打开的，那么返回的路径就会带有这个前缀。或者，如果 PowerShell 启动时的工作目录本身已经是扩展路径，那么 Python 继承了这个路径，导致输出带有前缀。

另一个可能性是，PowerShell 本身在某个配置下改变了当前目录的表示方式。比如，当使用 cd 命令进入一个路径时，如果路径很长，PowerShell 可能会自动使用扩展路径。这时候 Python 在获取当前目录时会得到这个格式。

为了验证，用户可以在 PowerShell 中运行其他命令，比如 pwd，看看显示的路径是否也有这个前缀。如果 PowerShell 本身的输出没有，那可能是 Python 的问题；如果 PowerShell 也显示同样的前缀，那就是系统环境的问题。

此外，检查 Python 的版本也很重要。较新的 Python 版本可能在处理 Windows 路径时更倾向于使用扩展路径，特别是如果系统启用了长路径支持的话。Windows 10 之后版本可以通过组策略启用长路径支持，这可能影响应用程序的行为。

总结一下，可能的原因是 Python 在获取当前工作目录时使用了扩展长度的路径格式，导致输出带有\\?\前缀。用户可以通过字符串处理去掉这个前缀，或者检查系统设置和 Python 版本，确认是否启用了长路径支持。另外，使用不同的方法获取路径，比如 os.path.abspath('.')，可能得到不同的结果。

</details>

在 Windows 系统中，当路径长度超过传统限制（260 字符）或某些特定条件触发时，Python 可能返回带有 `\\?\` 前缀的**扩展长度路径**（Extended-Length Path）。以下是详细解释及解决方法：

---

#### **原因分析**

1. **扩展路径前缀 `\\?\` 的作用**：
   - Windows 默认路径长度限制为 `MAX_PATH`（约 260 字符）。添加 `\\?\` 前缀后，系统允许路径长度扩展至约 **32767 字符**。
   - 该前缀直接告知系统禁用路径规范化（如自动解析符号链接），并绕过长度检查。

2. **Python 的路径获取机制**：
   - 当通过 `os.getcwd()` 获取当前目录时，若目录本身是通过扩展路径打开的，或系统/环境启用了长路径支持，Python 可能返回带有 `\\?\` 的格式。
   - 某些 Python 版本（如 3.6+）在支持长路径的 Windows 系统（如 Win10 1607+）中可能自动使用此格式。

3. **PowerShell 环境的影响**：
   - 若在 PowerShell 中通过特殊方式（如 `cd` 到超长路径或符号链接），可能导致工作目录以扩展路径形式传递到子进程（如 Python）。

---

#### **解决方案**

##### 1. 直接去除前缀（适用于路径未超长）

```python
import os
cwd = os.getcwd().replace(r'\\?\\', '')  # 移除前缀
print(cwd)
```

##### 2. 使用 `os.path.abspath('.')` 替代

```python
import os
print(os.path.abspath('.'))  # 通常返回不带前缀的标准路径
```

##### 3. 检查系统长路径支持设置

- **启用/禁用长路径支持**：
  1. 按 `Win+R` 输入 `gpedit.msc`。
  2. 导航至：`计算机配置 → 管理模板 → 系统 → 文件系统`。
  3. 检查 **“启用 Win32 长路径”** 是否启用。若启用，Python 可能更频繁返回扩展路径。

##### 4. 在代码中主动规范化路径

```python
import os
from pathlib import Path

cwd = Path(os.getcwd()).resolve()  # 解析符号链接并规范化路径
print(cwd)
```

---

#### **验证与调试**

- **在 PowerShell 中检查原始路径**：

  ```powershell
  # 直接打印当前目录（PowerShell 原生命令）
  pwd
  ```

  若此处也显示 `\\?\` 前缀，说明问题源于 PowerShell 环境或系统设置。

- **检查 Python 版本和系统更新**：
  - 更新到最新 Python 版本（某些旧版本存在路径处理差异）。
  - 确保 Windows 已安装最新更新（长路径支持可能依赖系统版本）。

---

#### **总结**

`\\?\` 前缀是 Windows 对超长路径的兼容性设计。虽然不影响路径有效性，但若需标准格式，可通过代码去除或调整系统设置。建议优先使用 `os.path.abspath('.')` 或 `pathlib` 库处理路径，以规避此类问题。

### 求证 deepseek

显然，这没有什么用，找了 2 个小时还没进展，很烦。

但我发现都是使用 watchexec 运行下出现的问题，尝试单独运行：

```console
$ watchexec -n python -c 'import os; print(os.getcwd()); import subprocess; subprocess.check_call(["""C:/Users/navyd/workspaces/projects/mise/target/debug/printenv.exe"""], env={})'
[Running: python -c import os; print(os.getcwd()); import subprocess; subprocess.check_call(["""C:/Users/navyd/workspaces/projects/mise/target/debug/printenv.exe"""], env={})]
\\?\C:\Users\navyd\workspaces\projects\navyd.github.io
current env dir: Ok("\\\\?\\C:\\Users\\navyd\\workspaces\\projects\\navyd.github.io")
all env:
```

没想到是 watchexec 出现的问题，参考 [UNC paths break CMD commands #830](https://github.com/watchexec/watchexec/issues/830) 在 [watchexec CLI v2.2.0](https://github.com/watchexec/watchexec/releases/tag/v2.2.0) 被修复。

而我目前所用 watchexec 的版本是 `2.1.2`，相差仅 1 个版本浪费了我多少精力！！！

### 原因

为何 watchexec 存在 [UNC 路径](https://learn.microsoft.com/zh-cn/dotnet/standard/io/file-path-formats#unc-paths) 这样的问题呢？

在 [Replace std::fs::canonicalize with dunce::canonicalize #858](https://github.com/watchexec/watchexec/pull/858) 中使用 [dunce](https://crates.io/crates/dunce) 库中的 [dunce::canonicalize](https://docs.rs/dunce/1.0.5/dunce/fn.canonicalize.html) 代替了 [std::fs::canonicalize](https://doc.rust-lang.org/std/fs/fn.canonicalize.html)。

这是由于 dunce 会尽可能将 Windows UNC 路径转换为 MS-DOS 兼容格式，而 rust 中的 `std::fs::canonicalize` 返回的 [extended length path](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file) 是 UNC 路径，而非常规 MS-DOS 兼容格式的路径，这才导致在 watchexec 下运行的程序也使用了 UNC 路径，而 mise 中的 `xx::file::glob` 显然是不支持 UNC 路径的，所以最后导致 `mise watch build` 运行失败。

## 解决

简单升级一下 watchexec 版本即可正常工作！

```console
$ watchexec -V
watchexec 2.3.0
$ watchexec -n python -c 'import os; print(os.getcwd()); import subprocess; subprocess.check_call(["""C:/Users/navyd/workspaces/projects/mise/target/debug/printenv.exe"""], env={})'
[Running: python -c import os; print(os.getcwd()); import subprocess; subprocess.check_call(["""C:/Users/navyd/workspaces/projects/mise/target/debug/printenv.exe"""], env={})]
C:\Users\navyd\Downloads\watchexec-2.3.0-x86_64-pc-windows-msvc
current env dir: Ok("C:\\Users\\navyd\\Downloads\\watchexec-2.3.0-x86_64-pc-windows-msvc")
all env:
```
