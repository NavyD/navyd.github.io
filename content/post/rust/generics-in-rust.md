---
title: "Generics in Rust"
date: 2022-03-06T10:07:19+08:00
draft: true
---

在rust中泛型可以做许多神奇的事，现在这里记录

<!--more-->

## 对其它类型添加方法

在[rbatis/src/crud.rs](https://github.com/rbatis/rbatis/blob/32ce4ecbcf92d7b66976d105364ea6a02412b2d3/src/crud.rs#L175)存在下面的实现

```rust
impl<T> CRUDTable for Option<T>
    where
        T: CRUDTable,
{
    fn table_name() -> String {
        T::table_name()
    }
//...
```

很奇怪，为什么对Option实现，难道可以添加到Option方法吗？使用下面的代码：

```rust
pub trait A {
    fn a(&self) {
        println!("a")
    }
}

impl<T> A for Option<T>
where
    T: A,
{
    fn a(&self) {
        println!("opt a")
    }
}

struct Aa {}
impl A for Aa {}

#[test]
fn test() {
    let v = Aa {};
    v.a(); // a
    let b = Some(v);
    b.a(); // opt a
}
```

`impl<T> CRUDTable for Option<T>`直接添加到`Option<T>`方法上，方便使用。

另外还有这样的`impl<T> CRUDTable for &T where T: CRUDTable {`是给`&T`添加方法，不过只能是tait中已存在的fn

## 自动添加trait

在[rust-websocket/websocket-base/src/stream.rs](https://github.com/websockets-rs/rust-websocket/blob/572693f78594adb86c80fcc208c1c40f9bded2f9/websocket-base/src/stream.rs#L10)中存在这样的，并对后面`std::net::TcpStream`实现了trait Stream

```rust
pub trait Stream: Read + Write {}
impl<S> Stream for S where S: Read + Write {}
```

由于TcpStream实现了Read与Write，这样为外部的struct实现了自定义的trait。下面的代码可以正常通过编译

```rust
use std::{io::{Read, Write}, mem::MaybeUninit, net::TcpStream};

pub trait Stream: Read + Write {}
impl<S> Stream for S where S: Read + Write {}

#[test]
fn test() {
    fn a(s: impl Stream) {}
    let v: MaybeUninit<TcpStream> = MaybeUninit::uninit();
    let s: TcpStream = unsafe {v.assume_init()};
    a(s)
}
```
