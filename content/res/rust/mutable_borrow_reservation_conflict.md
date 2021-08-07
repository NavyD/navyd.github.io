# mutable_borrow_reservation_conflict

## 描述

用map.get获取的值再+1插入时出现warning

```rust
fn dfs_counts(root: Option<Rc<RefCell<TreeNode>>>, counts: &mut HashMap<i32, u32>) {
    if let Some(root) = root {
        let root = root.borrow();
        match counts.get(&root.val) {
            Some(old_counts) => {
                // warning: cannot borrow `*counts` as mutable because it is also borrowed as immutable
                counts.insert(root.val, old_counts + 1)
            }
            None => counts.insert(root.val, 1),
        };
        Self::dfs_counts(root.left.clone(), counts);
        Self::dfs_counts(root.right.clone(), counts);
    }
}
```

```sh
warning: cannot borrow `*counts` as mutable because it is also borrowed as immutable
  --> src/find_mode_in_binary_search_tree.rs:50:25
   |
47 |                 match counts.get(&root.val) {
   |                       ------ immutable borrow occurs here
...
50 |                         counts.insert(root.val, old_counts + 1)
   |                         ^^^^^^                  ---------- immutable borrow later used here
   |                         |
   |                         mutable borrow occurs here
   |
   = note: `#[warn(mutable_borrow_reservation_conflict)]` on by default
   = warning: this borrowing pattern was not meant to be accepted, and may become a hard error in the future
   = note: for more information, see issue #59159 <https://github.com/rust-lang/rust/issues/59159>

```

## 原因

two-phase borrow

[Tracking issue for `mutable_borrow_reservation_conflict` compatibility lint #59159](https://github.com/rust-lang/rust/issues/59159)

## 方法

- 避免borrowed，Copy去除借用关系

```rust
let mut v = vec!["".to_string()];
if let Some(val) = v.get(0) {
    let a = val.to_string() + "new";
    v.push(a);
    // warning
    // v.push(val.to_string() + "new");
} else {
    v.push("new".to_string());
}
```

```rust
fn dfs_counts(root: Option<Rc<RefCell<TreeNode>>>, counts: &mut HashMap<i32, u32>) {
    if let Some(root) = root {
        let root = root.borrow();
        match counts.get(&root.val) {
            Some(old_counts) => {
                // // u32 is Copy so we copy it, new old_counts is not a reference owned by counts, so counts is not borrowed anymore
                let old_counts = *old_counts;
                counts.insert(root.val, old_counts + 1)
            }
            None => counts.insert(root.val, 1),
        };
        Self::dfs_counts(root.left.clone(), counts);
        Self::dfs_counts(root.right.clone(), counts);
    }
}
```

- 使用[Enty api](https://doc.rust-lang.org/nightly/std/collections/hash_map/enum.Entry.html)

```rust
fn dfs_counts(root: Option<Rc<RefCell<TreeNode>>>, counts: &mut HashMap<i32, u32>) {
    if let Some(root) = root {
        let root = root.borrow();
        // 封装match
        *counts.entry(root.val).or_insert(0) += 1;
        Self::dfs_counts(root.left.clone(), counts);
        Self::dfs_counts(root.right.clone(), counts);
    }
}
```

参考：

- [fold string to build hashmap char counter in rust, but gives two-phase borrow error
](https://stackoverflow.com/a/60663491/8566831)
- [Tracking issue for `mutable_borrow_reservation_conflict` compatibility lint #59159](https://github.com/rust-lang/rust/issues/59159)
