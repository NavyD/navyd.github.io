---
title: "Zsh History Encoding"
date: 2022-09-11T15:35:01+08:00
draft: false
tags: [zsh]
---

在使用python读取zsh_history输出时出现编码问题

```bash
$ python3 -c 'import sys; print(sys.stdin.read())' <~/.zsh_history
# Traceback (most recent call last):
#   File "<string>", line 1, in <module>
#   File "/usr/lib/python3.9/codecs.py", line 322, in decode
#     (result, consumed) = self._buffer_decode(data, self.errors, final)
# UnicodeDecodeError: 'utf-8' codec can't decode byte 0x81 in position 292191: invalid start by
```

<!--more-->

## 分析

找出当前出现问题的行后发现无法使用utf-8解码中文，打开是乱码，但使用history命令又是正常的

```sh
# ...
: 16......93:0;z Workspaces/learnings/惾�它�-箃...
: 16...8...6:0;bat 第14课丨3僯�...�解.docx
# ...
```

在这里[UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb8 in position 27: invalid start byte #2](https://github.com/rsalmei/zsh-history-to-fish/issues/2)提到这不是一个bug，是作为一种格式存储的：

> the history file is saved in metafied format

如果要解码，可以使用其提供的一个简单c程序

```c
#define Meta ((char) 0x83)

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>

/* from zsh utils.c */
char *unmetafy(char *s, int *len)
{
  char *p, *t;

  for (p = s; *p && *p != Meta; p++);
  for (t = p; (*t = *p++);)
    if (*t++ == Meta)
      t[-1] = *p++ ^ 32;
  if (len)
    *len = t - s;
  return s;
}

int main(int argc, char *argv[]) {
  char *line = NULL;
  size_t size;

  while (getline(&line, &size, stdin) != -1) {
    unmetafy(line, NULL);
    printf("%s", line);
  }

  if (line) free(line);
  return EXIT_SUCCESS;
}
```

下面是一个python版本[max747/pyzhist zsh history file decoder](https://gist.github.com/max747/4029742)，但实测没法解决开始提到的`0x81`错误

```python
def decodehist(_in, out):
    change = False
    for _c in _in.read():
        c = ord(_c)
        if c != 0x83:
            d = c^32 if change else c
            out.write(chr(d))
            change = False
        else:
            change = True

if __name__ == "__main__":
    import sys
    decodehist(sys.stdin, sys.stdout)
```

## 解决方案

考虑到我的实际需求并不是转换zsh history，而是解析是否存在内容并备份，不需要解析utf-8，可以在python作为byte处理即可

```python
import sys
reader = sys.stdin.buffer
writer = sys.stdout.buffer
```

参考：

* [Re: Fw: ZSH history file VS. UTF-8 data](https://www.zsh.org/mla/users/2011/msg00154.html)
* [如何更改 zsh 历史记录的编码？](https://segmentfault.com/q/1010000002517754)
* [UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb8 in position 27: invalid start byte #2](https://github.com/rsalmei/zsh-history-to-fish/issues/2)
* [max747/pyzhist zsh history file decoder](https://gist.github.com/max747/4029742)
