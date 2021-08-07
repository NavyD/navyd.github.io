# E0716: temporary value dropped while borrowed

在使用`chianed`链式调用时通常出现`E0716`借用编译错误。如

```rust
pub fn max_depth(root: Option<Rc<RefCell<TreeNode>>>) -> i32 {
    // compile failed: temporary value dropped while borrowed
    let root = queue.pop_front().unwrap().borrow();
}
```

编译上面代码错误：

```bash
$ cargo c          
    Checking leetcode-rust v0.1.0 (/home/navyd/Workspaces/projects/leetcode-rust)
error[E0716]: temporary value dropped while borrowed
  --> src/maximum_depth_of_binary_tree.rs:82:36
   |
82 |                         let root = queue.pop_front().unwrap().borrow();
   |                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^         - temporary value is freed at the end of this statement
   |                                    |
   |                                    creates a temporary which is freed while still in use
83 |                         // let root = root.borrow();
84 |                         if let Some(left) = root.left.clone() {
   |                                             ---- borrow later used here
   |
   = note: consider using a `let` binding to create a longer lived value

error: aborting due to previous error

For more information about this error, try `rustc --explain E0716`.
```

## 原因

以下面这段代码为例

```rust
// compile failed: temporary value dropped while borrowed
let foo = "FooBar".to_string().as_mut_str();
println!("{}", foo)
```

链式调用语法`desugar`后：

```rust
let foo = {
    let mut __temp = "FooBar".to_string();
    __temp.as_mut_str()
};
println!("{}", foo);
```

`__temp`在let scope后就不生效了drop，而`String::as_mut_str<'a>(&'a mut self) -> &'a mut str)`可变借用是依赖`__temp`的，如果rust允许foo存活，则foo就变成空指针了

如果要foo正常使用，则应该将`__temp`至少提升到foo一个scope上。

```rust
let mut foo = "FooBar".to_string();
let foo = foo.as_mut_str();
println!("{}", foo);
```

## 解法

分析原因后，只要改变scope即可：

```rust
pub fn max_depth(root: Option<Rc<RefCell<TreeNode>>>) -> i32 {
    let root = queue.pop_front().unwrap();
    let root = root.borrow();
}
```


## 参考

- [Can not understand: “temporary value dropped while borrowed”](https://users.rust-lang.org/t/can-not-understand-temporary-value-dropped-while-borrowed/23279/7)
- [Why `Option<&T>` will cause “temporary value dropped while borrowed”?](https://users.rust-lang.org/t/why-option-t-will-cause-temporary-value-dropped-while-borrowed/25581/3)
- [E0716](https://doc.rust-lang.org/error-index.html#E0716)
