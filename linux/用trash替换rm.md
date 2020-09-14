# 用trash替换rm

```bash
$ sudo apt-get install trash-cli
```

- trash-put           trash files and directories.
- trash-empty         empty the trashcan(s).
- trash-list          list trashed files.
- trash-restore       restore a trashed file.
- trash-rm            remove individual files from the trashcan.

## alias rm

```bash
alias rm='echo "rm is disabled, use remove or trash or /bin/rm instead."; false'
```

参考：

- [trash-cli](https://github.com/andreafrancia/trash-cli/)
- [Make `rm` move to trash](https://unix.stackexchange.com/questions/42757/make-rm-move-to-trash)
- [Best practices to alias the rm command and make it safer](https://superuser.com/questions/382407/best-practices-to-alias-the-rm-command-and-make-it-safer#:~:text=alias%20rm%3D'echo%20%22rm,your%20own%20safe%20alias%2C%20e.g.&text=or%20use%20trash%20instead.&text=You%20could%20try%20using%20trash%20instead.)
