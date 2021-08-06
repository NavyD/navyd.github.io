---
title: "git常用操作"
date: 2021-08-06T18:25:53+08:00
draft: false
---

## 撤消

### 删除本地最近的commit

[How do I undo the most recent local commits in Git?](https://stackoverflow.com/a/927386/8566831)

```sh
git commit -m "Something terribly misguided" # (0: Your Accident)
git reset HEAD~                              # (1) delete commit
git add .                                    # (3)
git commit -c ORIG_HEAD                      # (4)
```

如果之前未存在提交的文件，`git reset HEAD~`不会删除，只会将文件置为Unstaged changes，即`git add`前的状态

### 删除远程仓库的提交commits

[How to permanently remove few commits from remote branch](https://stackoverflow.com/a/41726152/8566831)

```sh
git reset --hard <last_working_commit_id>
git push --force
```
