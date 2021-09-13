---
title: "Docs"
date: 2021-08-26T14:10:14+08:00
draft: true
---

<!-- TODO -->

参考：

- [The rustdoc book](https://doc.rust-lang.org/stable/rustdoc/)
- [rust rfc 1946-intra-rustdoc-links](https://rust-lang.github.io/rfcs/1946-intra-rustdoc-links.html)

## 链接本地文件

参考：

- [Include images in rustdoc output #32104](https://github.com/rust-lang/rust/issues/32104)
- [embed-doc-image](https://crates.io/crates/embed-doc-image)

## 链接rust内部文档

As of Rust 1.48, you can now rely on RFC 1946. This adds the concept of intra-documentation links. This allows using Rust paths as the URL of a link:

- `[Iterator](std::iter::Iterator)`
- [Iterator][iter], and somewhere else in the document: [iter]: std::iter::Iterator
- [Iterator], and somewhere else in the document: [Iterator]: std::iter::Iterator

The RFC also introduces "Implied Shortcut Reference Links". This allows leaving out the link reference, which is then inferred automatically.

[std::iter::Iterator], without having a link reference definition for Iterator anywhere else in the document
``[`std::iter::Iterator`]``, without having a link reference definition for Iterator anywhere else in the document (same as previous style but with back ticks to format link as inline code)

参考：

- [How to link to other fns/structs/enums/traits in rustdoc?](https://stackoverflow.com/a/53504254/8566831)
