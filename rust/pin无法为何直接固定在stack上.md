# pin为何无法直接固定在stack上

在阅读[Futures Explained in 200 Lines of Rust](https://cfsamson.github.io/books-futures-explained/introduction.html)时，有一个疑问：为何不能在一个栈帧中创建一个自引用对象并返回它，因为任何指向“self”的指针都是无效的？

```rust
use std::pin::Pin;
use std::marker::PhantomPinned;

 #[derive(Debug)]
struct Test {
    a: String,
    b: *const String,
    _marker: PhantomPinned,
}


impl Test {
    fn new(txt: &str) -> Self {
        let a = String::from(txt);
        Test {
            a,
            b: std::ptr::null(),
            // This makes our type `!Unpin`
            _marker: PhantomPinned,
        }
    }
    fn init<'a>(self: Pin<&'a mut Self>) {
        let self_ptr: *const String = &self.a;
        let this = unsafe { self.get_unchecked_mut() };
        this.b = self_ptr;
    }

    fn a<'a>(self: Pin<&'a Self>) -> &'a str {
        &self.get_ref().a
    }

    fn b<'a>(self: Pin<&'a Self>) -> &'a String {
        unsafe { &*(self.b) }
    }
}
```

这是需要一个额外的`fn init<'a>(self: Pin<&'a mut Self>) {`方法，对pin的对象`Pin<&'a mut Self>`操作使field:`b`指针正确初始化

```rust
pub fn main() {
    // test1 is safe to move before we initialize it
    let mut test1 = Test::new("test1");
    // Notice how we shadow `test1` to prevent it from beeing accessed again
    let mut test1 = unsafe { Pin::new_unchecked(&mut test1) };
    Test::init(test1.as_mut());
     
    let mut test2 = Test::new("test2");
    let mut test2 = unsafe { Pin::new_unchecked(&mut test2) };
    Test::init(test2.as_mut());

    println!("a: {}, b: {}", Test::a(test1.as_ref()), Test::b(test1.as_ref()));
    println!("a: {}, b: {}", Test::a(test2.as_ref()), Test::b(test2.as_ref()));
}
```

有没有一个方法可以省去init方法在stack上直接Pin。

## 分析

首先尝试合并init方法到new方法中：

```rust
fn new(txt: &str) -> Option<Pin<Self>> {
    let a = String::from(txt);
    let mut t = Test {
        a,
        b: std::ptr::null(),
        // This makes our type `!Unpin`
        _marker: PhantomPinned,
    };
    let mut t = unsafe {Pin::new_unchecked(&mut t)};
    let ptr = &t.a as *const String;
    let this = unsafe { t.get_unchecked_mut()};
    this.b = ptr;
    None
}
```

要使new正确编译，首先要修改new的返回值定义：`-> Option<Pin<Self>> {`，上面的可以正常编译，但是最后如果要返回一个`Pin<Self>`时，没有方法可以直接做到。

来看下Pin的定义：`impl<P: Deref> Pin<P> {`

> A pinned pointer.
>
> This is a wrapper around a kind of pointer which makes that pointer “pin” its value in place...

构造方法：

```rust
pub unsafe fn new_unchecked(pointer: P) -> Pin<P> {}

pub fn new(pointer: P) -> Pin<P> {}
```

这些都在说明一件事，Pin是针对指针的，而rust从struct创建原始指针的方式只能通过`& T`和`&mut T`。在这里new是不能返回一个引用指针的，因为在stack上new退出后会被Drop

## 方案

### [pin_project](https://docs.rs/pin-project/1.0.7/pin_project/index.html)

在stack上提供pin

### Box::pin

Box也是一种指针，使用Box包装

```rust
fn new(txt: &str) -> Pin<Box<Self>> {
    let a = String::from(txt);
    let t = Test {
        a,
        b: std::ptr::null(),
        _marker: PhantomPinned,
    };
    let mut boxed = Box::pin(t);
    let self_ptr: *const String = &boxed.as_ref().a;
    unsafe { boxed.as_mut().get_unchecked_mut().b = self_ptr };

    boxed
}
```

参考：

* [Futures Explained in 200 Lines of Rust](https://cfsamson.github.io/books-futures-explained/introduction.html)
* [Primitive Type pointer](https://doc.rust-lang.org/std/primitive.pointer.html)
* [pin_project Original code: struct-default-expanded.rs](https://github.com/taiki-e/pin-project/blob/HEAD/examples/struct-default-expanded.rs)
