---
title: Wsl Install Error ERROR_INSTALL_FAILURE
date: 2025-02-16T13:03:21+08:00
draft: false
tags: [Windows, WSL2]
---

之前在 [wsl-update-error-REGDB_E_CLASSNOTREG](../wsl-update-error-REGDB_E_CLASSNOTREG/index.md) 中解决了更新错误后，莫名其妙开机给我自动更新了 WSL，然后又挂了！

```console
$ wsl
WSL 正在完成升级...
Warning 1946.Property 'System.AppUserModel.ToastActivatorCLSID' for shortcut 'WSL.lnk' could not be set.
Warning 1946.Property 'System.AppUserModel.IsSystemComponent' for shortcut 'WSL Settings.lnk' could not be set.
Could not write value  to key \SOFTWARE\Classes\Directory\Background\shell\WSL.   Verify that you have sufficient access to that key, or contact your support personnel.
wsl: WSL 安装似乎已损坏 (错误代码： Wsl/CallMsi/Install/ERROR_INSTALL_FAILURE)。
按任意键修复 WSL，或 CTRL-C 取消。
此提示将在 60 秒后超时。
正在将适用于 Linux 的 Windows 子系统更新到版本： 2.4.11。

$ wsl
wsl: WSL 安装似乎已损坏 (错误代码： Wsl/CallMsi/Install/REGDB_E_CLASSNOTREG)。
按任意键修复 WSL，或 CTRL-C 取消。
此提示将在 60 秒后超时。
正在将适用于 Linux 的 Windows 子系统更新到版本： 2.4.11。
```

## 解决

参考 [错误代码：Wsl/CallMsi/Install/REGDB_E_CLASSNOTREG #12282](https://github.com/Microsoft/wsl/issues/12282) 中提到 [triage/install-latest-wsl.ps1](https://github.com/microsoft/WSL/blob/8c61f09e4d28995a3827f71e03332b5257e16418/triage/install-latest-wsl.ps1#L35-L42)

1. 下载最新的 [WSL/releases](https://github.com/microsoft/WSL/releases)
2. 以管理员权限打开 powershell
3. 修改`$target="your wsl.msi path"`后运行下面的代码

    ```powershell
    $target = "C:\Users\xxxx\Downloads\wsl.2.4.11.0.x64.msi"
    $MSIArguments = @(
        "/i"
        $target
        "/qn"
        "/norestart"
    )
    Start-Process -Wait "msiexec.exe" -ArgumentList $MSIArguments -NoNewWindow -PassThru
    ```

安装完成后即可正常打开 WSL，但是否像之前一样下次更新又挂了，就看微软给不给力了，到时候别再加更几期大家一起看连续剧！
