---
title: "Recursive Type in Rust"
date: 2022-04-07T13:03:54+08:00
draft: true
---

编译递归类型的struct时出现错误：

```rust
struct Node {
    is_end: bool,
    children: [Option<Node>; 26],
}
// error:
// recursive type `implement_trie_prefix_tree::solution_node::Node` has infinite size
// recursive type has infinite sizerustcE0072
```

<!--more-->

<!-- TODO -->

参考：

* [rust error: E0072](https://doc.rust-lang.org/error-index.html#E0072)
