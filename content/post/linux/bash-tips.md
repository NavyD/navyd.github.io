---
title: "Bash Tips"
date: 2022-09-05T11:27:47+08:00
draft: true
---

bash tips

<!--more-->

## heredoc `<<,<<<`

保存文字里面的换行或是缩进等空白字元。允许在字符串里执行变量替换和命令替换。

```bash
# shell变量替换
python3 <<EOF
distinct_paths = list(dict.fromkeys('$PATH'.split(':')))
print(':'.join(distinct_paths))
EOF
# stdout: /usr/local/sbin:/usr/local/bin:...

# 禁用shell变量替换
cat << 'EOF'
Working dir $PWD
EOF
# stdout: Working dir $PWD


# tab缩进格式手动\t替换为tab，空格将失败，在现代基本不用
python3 <<-EOF
\t  distinct_paths = list(dict.fromkeys('$PATH'.split(':')))
\t  print(':'.join(distinct_paths))
EOF
# stdout: /usr/local/sbin:/usr/local/bin:...
```

参考：

* [How can I write a heredoc to a file in Bash script?](https://stackoverflow.com/a/2954835/8566831)
* [Advanced Bash-Scripting Guide: Chapter 19. Here Documents](https://tldp.org/LDP/abs/html/here-docs.html)
* [wiki: Here 文档](https://zh.wikipedia.org/wiki/Here%E6%96%87%E6%A1%A3)
