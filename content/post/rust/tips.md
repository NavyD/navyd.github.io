---
title: "Tips"
date: 2021-12-04T21:28:06+08:00
draft: true
---

<!--more-->
## 迭代器

### result in iter

使用`iter()`函数式循环中在map时出现Result或Option时，collect时可能需要直接停止并返回Result,Option。

通常是返回`collect::<Vec<_>>()`，其返回类型实际是`Vec<Result<_, _>>`，无法在error时停止

```rust
// Vec<Result<_, _>>
let numbers = ["tofu", "93", "18"]
    .into_iter()
    .map(|s| s.parse::<i32>())
    .collect::<Vec<_>>();
```

可以使用`collect::<Result<Vec<_>>>()`返回Result在err时停止的

```rust
// Result<_, Vec<_>>
let numbers = ["tofu", "93", "18"]
    .into_iter()
    .map(|s| s.parse::<i32>())
    .collect::<Result<Vec<_>, _>>();
```

参考：

* [Rust By Example: Fail the entire operation with collect()](https://doc.rust-lang.org/rust-by-example/error/iter_result.html#fail-the-entire-operation-with-collect)

## IO

### array to Read

* [How to read (std::io::Read) from a Vec or Slice?](https://stackoverflow.com/a/60586574/8566831)
* [std::io::Cursor](https://doc.rust-lang.org/std/io/struct.Cursor.html)
