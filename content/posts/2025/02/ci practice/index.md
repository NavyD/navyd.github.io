---
title: CI Practice
date: 2025-02-18T14:04:55+08:00
draft: false
tags: [CI, git, git hook, lint, DevOps]
---

## git hook manager

- [evilmartians/lefthook: Fast and powerful Git hooks manager for any type of projects](https://github.com/evilmartians/lefthook)
- [pre-commit/pre-commit: A framework for managing and maintaining multi-language pre-commit hooks](https://github.com/pre-commit/pre-commit)

参考：

- [Lefthook 的五种武器](https://xfyuan.github.io/2024/06/five-cool-and-surprising-ways-to-configure-lefthook-for-automation-joy/)
- [5 cool (and surprising) ways to configure Lefthook for automation joy](https://evilmartians.com/chronicles/5-cool-and-surprising-ways-to-configure-lefthook-for-automation-joy)

### lefthook

#### 并行

在 pre-commit 时通常会存在检查与修复操作，一个问题，并行处理同一个文件且都尝试更新时，如何处理竞争条件。

配置 [parallel](https://lefthook.dev/configuration/parallel.html#parallel) 可以让 [`commands`](https://lefthook.dev/configuration/Commands.html#commands) [Scripts](https://lefthook.dev/configuration/Scripts.html#scripts) [`jobs`](https://lefthook.dev/configuration/jobs.html#jobs) 类型的任务并行，但有时对其中某些特定的任务是需要先后顺序的，如所有的 lint 可以并行，但 fixed 通常需要在 lint 后执行避免竞争

##### jobs

参考 [Differences from Commands and Scripts](https://lefthook.dev/configuration/jobs.html#differences-from-commands-and-scripts) 提供了 job 组的概念，分组后 jobs 并行串行可组合方便

#### run with shell

在运行命令 [`run: command list`](https://lefthook.dev/configuration/run.html) 时无法指定 shell，`*nix`, `windows` 不兼容语法，只能使用 [scripts](https://lefthook.dev/configuration/Scripts.html) 文件执行，对于某些简单的命令非常不方便。

如检查文件名在 windows 上是否合法参考 [# Add check for illegal Windows filenames](https://github.com/pre-commit/pre-commit-hooks/issues/589) 使用 `(?i)((^|/)(CON|PRN|AUX|NUL|COM[\d¹²³]|LPT[\d¹²³])(\.|/|$)|[<>:\"\\|?*\x00-\x1F]|/[^/]*[\.\s]/|[^/]*[\.\s]$)` 正则检查时需要创建文件而不能在 yaml 文件中写简单 python 的代码。

另外，在 `run: command to {staged_files}` 看起来也非常不稳定，使用 [quotes](https://lefthook.dev/configuration/run.html#quotes) 处理模板，可能存在转义的问题

参考：

- [# Wrap commands in Git bash on Windows](https://github.com/evilmartians/lefthook/issues/953)
- [# Invalid escaping of {staged_files}](https://github.com/evilmartians/lefthook/issues/786)

## lint

### yaml

#### schema

在 [JSON Schema Store](https://www.schemastore.org/json/) 中提供了 schema 结构以方便检查

yamllint 不支持验证 [Support to validate against a schema](https://github.com/adrienverge/yamllint/issues/37)

[redhat-developer/yaml-language-server](https://github.com/redhat-developer/yaml-language-server) 虽然支持验证 [Using inlined schema](https://github.com/redhat-developer/yaml-language-server#using-inlined-schema) 如 `# yaml-language-server: $schema=<urlToTheSchema>` ，但未提供 cli 接口运行 [Command Line API/Option](https://github.com/redhat-developer/yaml-language-server/issues/535)

参考：

- [How do I validate my YAML file from command line?](https://stackoverflow.com/questions/3971822/how-do-i-validate-my-yaml-file-from-command-line)

### git commit message

- [conventional-changelog/commitlint: Lint commit messages](https://github.com/conventional-changelog/commitlint)
- [commitizen-tools/commitizen: Create committing rules for projects 🚀 auto bump versions ⬆️ and auto changelog generation](https://github.com/commitizen-tools/commitizen)

注意：对于非 js 项目 `npm install --save-dev @commitlint/config-conventional @commitlint/cli` 是无法使用的
