---
title: Daemon Process in Windows
date: 2025-02-14T22:20:57+08:00
draft: false
tags: [windows, daemon, process, python, chat, LLM]
---

在 windows 上进入一个目录后启动一个守护进程如`hugo server`服务，方便在浏览器中实时查看内容更新。虽然 daemon 进程在 unix 系统中很常见，但在 windows 中并没有这样的概念，在 powershell 中存在一个 [Start-Process](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/start-process?view=powershell-7.4) 命令可以启动一个后台进程，即使关闭终端也可以保持在后台运行

```powershell
Start-Process java -ArgumentList '-jar', 'MyProgram.jar' -RedirectStandardOutput '.\console.out' -RedirectStandardError '.\console.err'
```

如何使用 python 实际类似的功能呢？

## 分析

### deepseek

在 python 中如何启动一个进程 A 并将其附加到当前 python 进程 B 的父进程 C 中，以避免当前 python 进程 B 退出后进程 A 也被终止。我知道在 unix 系统上用 daemon 进程和在 windows 系统上用 detached 进程可以将子进程 A 转为后台进程以避免当前 Python 进程 B 退出后被终止，但我想要的启动当前 python 进程 B 的父进程 C 在 python 进程 B 退出后接管子进程 A，此时子进程 A 仍然存活，而当进程 C 退出时终止子进程 A。注意：要求兼容 windows 与 unix 系统

<details>
    <summary>Thinking Process (101s):</summary>
嗯，用户的问题是关于如何在 Python 中启动一个进程 A，并将其附加到当前进程 B 的父进程 C 中，这样当进程 B 退出时，进程 A 不会被终止，而是由父进程 C 接管，当 C 退出时，进程 A 才会终止。用户希望这个方案同时兼容 Windows 和 Unix 系统。

首先，我需要理解进程的父子关系。通常，子进程的父进程是启动它的那个进程。当父进程终止时，子进程会成为孤儿进程，由 init（在 Unix）或系统进程（Windows）接管，这样它们就不会被终止。但用户的情况不同，他希望进程 A 在进程 B 退出后，被进程 C 接管，也就是进程 B 的父进程，而不是系统的 init 或类似进程。

用户提到，使用 daemon 进程或在 Windows 上使用 detached 进程可以让子进程在后台运行，避免被父进程终止。但这里的需求是让父进程的父进程（即祖先进程）来接管子进程 A，这可能涉及到修改进程的父进程 ID，这在常规的操作系统中可能不容易实现，因为进程的父进程 ID 通常由操作系统管理，不能随意更改。

接下来，我需要考虑如何在 Python 中实现这一点。可能需要使用平台特定的方法，因为 Windows 和 Unix 系统的进程管理机制不同。例如，在 Unix 系统中，可能可以使用双重分叉（double fork）的技术来使子进程成为 init 的子进程，这样原来的父进程退出后，子进程由 init 接管。而在 Windows 系统中，可能需要设置 CREATE_NEW_PROCESS_GROUP 或者使用 detached 标志来创建独立的进程。

但用户的需求并不是让子进程成为 init 的子进程，而是成为当前进程的父进程（进程 C）的子进程。这可能涉及到在启动子进程 A 时，直接让进程 C 成为其父进程。但如何在 Python 中实现这一点呢？

可能需要先获取当前进程 B 的父进程 ID（进程 C 的 PID），然后在启动进程 A 时，以某种方式将其父进程设置为进程 C 的 PID。不过，修改子进程的父进程通常需要操作系统级别的调用，比如在 Unix 中使用 os.setppid()，但 Python 的标准库中可能没有这样的函数。因此，可能需要使用平台特定的方法，如 Unix 中的 fork 和 setsid，或者 Windows 中的 Job 对象或其他机制。

在 Unix 系统中，当父进程退出后，子进程会被 init 接管，但用户希望的是被进程 C 接管。这可能意味着进程 B 需要以某种方式将子进程 A 的父进程更改为进程 C。但进程 B 无法直接修改其他进程的父进程，除非有权限使用像 prctl 这样的系统调用，或者通过某种中间步骤，如让进程 C 主动收养进程 A。

或许，可以通过让进程 C 在启动进程 B 时，预先设置某种信号处理，当进程 B 退出时，进程 C 接管进程 A。但这需要进程 C 的配合，而用户的问题中并没有提到可以修改进程 C 的行为，因此这可能不可行。

另一个思路是，当进程 B 启动进程 A 时，让进程 A 脱离进程 B，成为进程 C 的子进程。这可能需要进程 A 在启动后立即将其父进程更改为进程 C。例如，在 Unix 系统中，可以通过双重分叉，使得进程 A 成为孤儿进程，被 init 接管，但这里需要被进程 C 接管，这可能不可行，除非进程 C 主动调用 wait 或类似的函数来收养子进程，但这似乎不太可能。

或许，正确的做法是让进程 A 在启动时直接由进程 C 启动，而不是由进程 B 启动。但这样的话，进程 B 就无法控制进程 A 的启动。但用户的需求是进程 B 启动进程 A，然后将其父进程设置为进程 C。

可能需要跨平台的解决方案，结合 Unix 和 Windows 的不同方法。例如，在 Unix 中使用双重分叉使子进程成为孤儿，由 init 接管，但用户希望由进程 C 接管，这可能无法实现。或者，是否可能让进程 B 启动进程 A，然后进程 A 将自己重新父级到进程 C？这可能需要特定的系统调用，如 Linux 中的 prctl(PR_SET_CHILD_SUBREAPER) 或者类似的功能，但不确定是否跨平台。

另外，Windows 中的作业对象可能可以用来管理进程的生命周期，但同样需要特定的处理。可能需要使用 CreateProcess 函数中的某些标志，如 CREATE_BREAKAWAY_FROM_JOB，让进程 A 脱离进程 B 的作业，从而在进程 B 退出后继续运行。但这需要特定的 Windows API 调用，而 Python 可能通过 ctypes 或 win32api 模块来实现。

总结来说，可能的解决方案是：

1. 在 Unix 系统中，使用双重分叉来使进程 A 成为 init 的子进程，这样进程 B 退出后，进程 A 仍然存活，由 init 接管。但这不符合用户希望由进程 C 接管的要求，因为 init 是进程 C 的父进程吗？可能用户的问题中存在误解，可能用户认为进程 B 的父进程 C 在进程 B 退出后接管进程 A，而实际上在 Unix 中，孤儿进程会被 init 接管，而不是原来的父进程。

因此，可能用户的需求实际上无法直接实现，因为进程的父进程关系在创建时确定，之后不能更改，除非特定系统支持。因此，可能的解决方案是让进程 A 在启动时脱离进程 B，使其成为后台进程，这样当进程 B 退出时，进程 A 继续运行，由系统的 init 或相应进程接管，而不是由进程 C 接管。但用户明确希望由进程 C 接管，这可能不可行。

或者，用户可能误解了进程的父子关系。例如，如果进程 B 的父进程是 C，当 B 启动进程 A，正常情况下 A 的父进程是 B。当 B 退出，A 的父进程变为 init（或类似进程），而不是 C。所以用户希望的是，当 B 退出后，A 的父进程变为 C，而不是 init。这需要操作系统支持重新设置父进程，这在常规情况下是不可能的，除非使用某些特定的方法，如 prctl 设置 subreaper，但这可能仅限于 Linux，并且需要权限。

因此，可能正确的结论是，无法跨平台实现用户的需求，即让进程 A 在进程 B 退出后被进程 C 接管。替代方案是让进程 A 成为守护进程或独立进程，这样当进程 B 退出时，进程 A 继续运行，但其父进程变为 init 或系统进程，而不是进程 C。这可能接近用户的需求，但不完全符合。

因此，可能的解决方案是：在启动进程 A 时，使其成为独立进程，脱离进程 B，这样当进程 B 退出时，进程 A 继续运行，由系统接管。虽然父进程不是 C，但至少不会被 B 的退出而终止。而进程 C 退出时，系统会终止所有子进程，所以如果进程 A 的父进程是系统进程（如 init），那么当 C 退出时，进程 A 不会被终止，这可能与用户的需求不符，因为用户希望当 C 退出时，进程 A 也被终止。

这里可能存在用户的需求矛盾。如果希望当 C 退出时，进程 A 也被终止，那么进程 A 必须作为 C 的子进程。但用户希望进程 A 由 B 启动，同时成为 C 的子进程，这样当 B 退出后，进程 A 仍然作为 C 的子进程存在，当 C 退出时，进程 A 被终止。这需要进程 A 在启动时，父进程直接设置为 C，而不是 B。但如何做到这一点？

在 Unix 系统中，进程的父进程是在 fork 时确定的，无法在之后更改。因此，如果进程 B 要启动进程 A 并让 C 成为其父进程，这可能需要进程 C 主动调用 fork 或者类似的方法，但这需要进程 B 和 C 之间有某种通信机制，例如进程 B 通知进程 C 去启动进程 A，但这超出了进程 B 自身启动进程 A 的情况。

或者，使用某种中间进程，例如进程 B 创建一个脚本或执行命令，让进程 C 来启动进程 A，但这需要进程 C 的主动参与，可能不现实。

综上，可能用户的需求在常规的操作系统进程管理机制下无法实现，因为子进程的父进程一旦创建就无法更改，除非使用特定于平台的复杂方法，而这样的方法可能无法跨平台兼容。因此，可能的结论是，无法在 Python 中跨平台实现用户的需求，即启动一个进程 A，其父进程是当前进程 B 的父进程 C，这样当 B 退出后，A 仍然由 C 管理，并在 C 退出时终止。

不过，用户可能实际的需求是让进程 A 独立于进程 B，不被 B 的退出所终止，同时在进程 C（B 的父进程）退出时，进程 A 也被终止。这种情况下，进程 A 需要成为进程 C 的子进程。但如何让进程 B 启动一个子进程 A，而 A 的父进程是 C？

可能的解决方案是，进程 B 通过某种方式让进程 C 来启动进程 A。例如，进程 B 可以发送信号或请求给进程 C，让进程 C 执行启动进程 A 的操作。这需要进程 C 有监听和处理这样的请求的能力，比如通过进程间通信（IPC）机制。这可能超出了仅用 Python 代码在进程 B 内部解决问题的范围。

因此，可能正确的答案是，无法直接通过 Python 的标准库或常见跨平台方法实现用户的需求。替代方案是让进程 A 成为守护进程或独立进程，从而在进程 B 退出后继续运行，但其父进程变为系统的 init 进程，而不是进程 C。此时，当进程 C 退出时，不会影响进程 A，这与用户的要求不符。因此，用户的需求可能无法满足。

但用户提到知道 daemon 和 detached 进程的方法，但希望进程 A 被进程 C 接管。可能用户存在误解，认为进程 C 会自然接管进程 A，但实际上当 B 退出后，A 的父进程是 init，而不是 C。所以，可能用户需要的是让进程 A 成为进程 C 的子进程，这只能在进程 C 主动创建进程 A 的情况下实现，而不是由进程 B 创建。因此，可能需要重新设计进程的启动流程，让进程 C 直接创建进程 A，而不是通过进程 B。或者，如果进程 B 必须创建进程 A，则可能无法满足父进程为 C 的条件。

因此，可能的最终结论是，无法在跨平台的情况下实现用户的需求。建议用户重新考虑设计，或者接受进程 A 由系统接管，而不是进程 C。
</details>

#### Assistant

在操作系统中，进程的父子关系一旦建立就无法直接更改，因此无法直接将子进程 A 的父进程动态修改为当前进程 B 的父进程 C。但可以通过以下跨平台方案让子进程 A 在进程 B 退出后继续运行，并确保其生命周期与进程 C 一致：

#### 跨平台解决方案

```python
import sys
import subprocess
import os

def start_detached_process(command):
    if sys.platform == 'win32':
        # Windows 使用 DETACHED_PROCESS 和 CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(
            command,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True
        )
    else:
        # Unix 使用双 fork 脱离进程组
        if os.fork() == 0:
            os.setsid()
            if os.fork() == 0:
                subprocess.Popen(command, start_new_session=True)
            os._exit(0)
        os.wait()

# 示例用法
start_detached_process(["python", "child_process.py"])
```

#### 方案说明

1. **Windows**:
   - 使用 `DETACHED_PROCESS` 和 `CREATE_NEW_PROCESS_GROUP` 标志创建独立进程。
   - 新进程会脱离当前进程 B 的控制，在进程 B 退出后继续运行。
   - 进程 A 的生命周期不再依赖进程 B，但也不会自动关联进程 C。

2. **Unix**:
   - 通过双重分叉 (`double fork`) 创建守护进程。
   - 使用 `os.setsid()` 创建新会话，彻底脱离进程 B 的控制。
   - 子进程 A 将成为系统级后台进程（父进程为 init/systemd）。

#### 生命周期控制

- **进程 B 退出时**：子进程 A 继续存活，但父进程变为系统进程（而非进程 C）。
- **进程 C 退出时**：若希望进程 A 随之终止，需通过进程间通信（如信号、套接字）实现。例如：
  - 进程 C 启动时监听特定信号。
  - 进程 A 定期检查进程 C 是否存在（通过 PID 或心跳机制）。
  - 进程 C 退出时主动通知进程 A 终止。

#### 关键点

- **无法直接修改父进程**：操作系统不允许动态修改进程父子关系。
- **依赖系统托管**：脱离后的进程由系统托管，与进程 C 无直接关联。
- **需额外逻辑关联 C 的生命周期**：需通过 PID 检查或 IPC 机制实现进程 A 与 C 的生命周期绑定。

建议通过进程间通信实现逻辑上的生命周期绑定，而不是依赖操作系统的进程树机制。

### 求证

在 windows 中使用 win32 [Process Creation Flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags) 创建即可

```python
import subprocess
# 配置启动信息以隐藏窗口
stdout_path = ".hugo-server.log"
with open(stdout_path, "wb") as stdout:
    stderr = stdout
    proc = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=stdout,
        stderr=stderr,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
```

参考：

- [Start a detached background process in PowerShell](https://stackoverflow.com/a/25035181/8566831)
- [Call a python subprocess as daemon and exit](https://stackoverflow.com/a/8947742/8566831)
- [How to detach Python child process on Windows (without setsid)?](https://stackoverflow.com/a/52450172/8566831)
- [How to start daemon process from python on windows?](https://stackoverflow.com/a/12854376/8566831)
- [Python - Launch detached process, wait for specific output in stdout, then continue](https://stackoverflow.com/a/67940259/8566831)
