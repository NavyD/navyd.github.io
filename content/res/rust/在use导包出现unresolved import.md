# 在use导包出现unresolved import

在vscode rust analyzer使用另一个mod时无法导入，出现错误：`unresolved importrust-analyzer`，下面是包结构：

```
── src
   ├── lib.rs
   ├── main.rs
   └── youdao_client.rs
```

```rust
//lib.rs
pub mod youdao_client;
```

```rust
// main.rs
use crate::youdao_client::YoudaoClient
```

```toml
[package]
name = "youdao-dict-export"
```

## 原因

这里直接引用[Cargo build shows unresolved import](https://users.rust-lang.org/t/cargo-build-shows-unresolved-import/45445/7)中一段：

> Projects that have both a lib.rs and a main.rs are actually compiled ***as two seperate crates*** - one library, and a binary that implicitly depends on that library. Your mod declarations are in main.rs, so they are part of the binary crate, not the library crate.

main.rs与lib.rs已经是两个crate，不能直接以`use crate::youdao_client::YoudaoClient`导入

## 解法

### use crate_name

lib已经是独立的crate，那就可以用use crate_name导入：

```rust
// main.rs
use youdao_dict_export::*;
```

rust自动处理crate name`-`到mod `_`的转换

### mod

不分离两个crate，删除lib.rs，使用mod组合即可

```rust
// main.rs
mod youdao_client;

use crate::youdao_client::*;
```

## 参考

- [Cargo build shows unresolved import](https://users.rust-lang.org/t/cargo-build-shows-unresolved-import/45445/7)
