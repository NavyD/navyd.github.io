---
title: "How to Embed a Static Variable Into Documentation"
date: 2021-11-13T00:54:17+08:00
draft: false
tags: [rust, doc]
---

在编写rust文档时可能需要用到编译时静态变量的值，如环境变量`env!("CARGO_PKG_NAME")`等

<!--more-->

## Declarative Macros

```rust
macro_rules! impl_foo {
    ($name:ident, $sname:expr) => {
        #[doc = "Returns a new `"]
        #[doc = $sname]
        #[doc = "`."]
        pub fn myfoo() -> $name {
            42
        }
    };

    ($name:tt) => {
        impl_foo!($name, stringify!($name));
    };
}

impl_foo!(u32);
```

参考：

* [How to embed a Rust macro variable into documentation?](https://stackoverflow.com/a/43353854/8566831)
* [How to create a static string at compile time](https://stackoverflow.com/a/32956193/8566831)
* [The rustdoc book: The #[doc] attribute](https://doc.rust-lang.org/rustdoc/the-doc-attribute.html)
* [impl: Attribute Macro embed_doc_image::embed_doc_image](https://docs.rs/embed-doc-image/0.1.4/src/embed_doc_image/lib.rs.html#297-340)
