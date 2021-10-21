---
title: "Script Encoding in Python"
date: 2021-10-21T15:56:52+08:00
draft: true
tags: [python, encoding, script]
---

在python脚本中通常能看到下面的声明：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ...
```

这是由于在python2.5前源码字符串literal使用Latin-1编码，如果出现非 ASCII 字符且未声明源编码，则会出现错误。

<!--more-->

这种问题在python3已不需要，在PEP 3120中使用utf8作为默认编码

参考：

* [Working with UTF-8 encoding in Python source [duplicate]](https://stackoverflow.com/a/6289494/8566831)
* [PEP 263 -- Defining Python Source Code Encodings](https://www.python.org/dev/peps/pep-0263/#defining-the-encoding)
* [PEP 3120 -- Using UTF-8 as the default source encoding](https://www.python.org/dev/peps/pep-3120/)
