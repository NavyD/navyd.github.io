---
title: "Request coalescing in async Rust"
date: 2022-3-14T05:07:15+08:00
tags: [rust, http, tracing, tokio, axum]
draft: true
---

As the popular saying goes, there are only two hard problems in computer science: caching, off-by-one errors, and getting a Rust job that isn't cryptocurrency-related.

Today, we'll discuss caching! Or rather, we'll discuss... "request coalescing", or "request deduplication", or "single-flighting" - there's many names for that concept, which we'll get into fairly soon.

That is, as soon as we set the stage...

A simple web server
-------------------

I don't publish the source code for [my website](https://fasterthanli.me/). I try to concentrate on writing articles and producing videos. I do have a ton of proprietary code, though: over 8000 lines (according to [tokei](https://lib.rs/crates/tokei)) for the web server alone.

But I don't want to spend the time to maintain it _for everyone_, and every possible use case, and burn myself out just doing that maintenance work, instead of writing new articles. So I can't point you at the repository and go"here, just do that"!

Instead, let's write a simple version of just the parts we need to get into today's topic.

And that part is... a web server. My actual website is powered by [warp](https://lib.rs/crates/warp), but I'm planning to migrate to [axum](https://lib.rs/crates/axum) pretty quickly, so let's pretend it's already done and use that.

Living in fantasy land again, are we.

So first, a hello world:

```
$ cargo new plaque
     Created binary (application) `plaque` package

$ cd plaque

$ cargo run
   Compiling plaque v0.1.0 (/home/amos/bearcove/plaque)
    Finished dev [unoptimized + debuginfo] target(s) in 0.37s
     Running `target/debug/plaque`
Hello, world!
```

Okay, that was easy. It doesn't serve web requests though!

To serve web requests, we'll want to be able to do async I/O. We don't _have_ to: we could just do blocking I/O.

Here, let me show you:

```
use std::{
    error::Error,
    io::{Read, Write},
    net::{SocketAddr, TcpListener},
};

fn main() -> Result<(), Box<dyn Error>> {
    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    let listener = TcpListener::bind(addr)?;
    println!("Listening on http://{}", addr);
    loop {
        let (mut stream, addr) = listener.accept()?;
        println!("Accepted connection from {addr}");

        let mut incoming = vec![];

        loop {
            let mut buf = vec![0u8; 1024];
            let read = stream.read(&mut buf)?;
            incoming.extend_from_slice(&buf[..read]);

            if incoming.len() > 4 && &incoming[incoming.len() - 4..] == b"\r\n\r\n" {
                break;
            }
        }

        let incoming = std::str::from_utf8(&incoming)?;
        println!("Got HTTP request:\n{}", incoming);
        stream.write_all(b"HTTP/1.1 200 OK\r\n")?;
        stream.write_all(b"\r\n")?;
        stream.write_all(b"Hello from plaque!\n")?;
        println!("Closing connection for {addr}");
    }
}
```

This works! I had to repress _several_ urges to finish writing this, but it does, in fact, work:

```
# In terminal 1
$ cargo run --quiet
Listening on http://0.0.0.0:3779

# In terminal 2
$ curl http://0.0.0.0:3779
Hello from plaque!

# Meanwhile, in terminal 1
Accepted connection from 127.0.0.1:34594
Got HTTP request:
GET / HTTP/1.1
Host: 0.0.0.0:3779
User-Agent: curl/7.79.1
Accept: */*


Closing connection for 127.0.0.1:34594
```

It even works from an actual web browser!

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/everyone-loves-edge-right.8840c51826622d31.jpg) 

But it's not... good.

The case for async
------------------

There's many not-so-good things about this web server (turns out there's a lot of depth to handling HTTP properly), but there's a glaring one: it can only service one client at a time.

If we were to use netcat to open a TCP connection to our server, send a single HTTP request and just wait, it would prevent anyone else from connecting to the server.

See, at first our server is blocked in an `accept4` syscall:

```
$ rust-gdb -quiet -pid $(pidof plaque) -ex "t a a bt" -ex "set confirm off" -ex "q" | 2>/dev/null | grep -A 90 'Thread 1' | grep -vE '[dD]etach(ing|ed)'
Thread 1 (Thread 0x7f7c481d7780 (LWP 775276) "plaque"):
#0  0x00007f7c482ed6aa in accept4 (fd=3, addr=..., addr_len=0x7ffdb31011ac, flags=524288) at ../sysdeps/unix/sysv/linux/accept4.c:32
#1  0x0000558267510329 in std::sys::unix::net::{impl#0}::accept::{closure#0} () at library/std/src/sys/unix/net.rs:225
#2  std::sys::unix::cvt_r<i32, std::sys::unix::net::{impl#0}::accept::{closure#0}> () at library/std/src/sys/unix/mod.rs:212
#3  std::sys::unix::net::Socket::accept () at library/std/src/sys/unix/net.rs:225
#4  std::sys_common::net::TcpListener::accept () at library/std/src/sys_common/net.rs:407
#5  std::net::tcp::TcpListener::accept () at library/std/src/net/tcp.rs:811
#6  0x00005582674fac75 in plaque::main () at src/main.rs:12
```

The command above runs GDB (well, a wrapper for GDB that loads some Rust-specific scripts) in quiet mode, attaches to the given PID (process id), which is the PID of the only running instance of "plaque", our sample application, then we run GDB command "t a a bt" (thread apply all backtrace), then exit gdb, then pipe all of that through a couple greps to clean up the output a little.

And once it accepts a connection, it's blocked in a `read` syscall:

```
$ rust-gdb -quiet -pid $(pidof plaque) -ex "t a a bt" -ex "set confirm off" -ex "q" | 2>/dev/null | grep -A 90 'Thread 1' | grep -vE '[dD]etach(ing|ed)'
Thread 1 (Thread 0x7f7c481d7780 (LWP 775276) "plaque"):
#0  0x00007f7c482ed030 in __libc_recv (fd=4, buf=0x558267afeba0, len=1024, flags=0) at ../sysdeps/unix/sysv/linux/recv.c:28
#1  0x0000558267510594 in std::sys::unix::net::Socket::recv_with_flags () at library/std/src/sys/unix/net.rs:245
#2  std::sys::unix::net::Socket::read () at library/std/src/sys/unix/net.rs:251
#3  std::sys_common::net::UdpSocket::recv () at library/std/src/sys_common/net.rs:638
#4  std::net::udp::UdpSocket::recv () at library/std/src/net/udp.rs:693
#5  0x00005582674faf26 in plaque::main () at src/main.rs:19
```

Yes, yes, that makes sen- wait is that `UdpSocket` in the backtrace?

Yeah so, funny story: you know how sometimes people say "code optimizations make it harder to debug"?

That's one of these cases. Turns out if you have two functions with the exact same code, LLVM [only generates one](https://godbolt.org/z/WhG8GnEc6).

Interestingly enough, if we dig a little with GDB:

```
(gdb) frame 3
#3  std::sys_common::net::UdpSocket::recv () at library/std/src/sys_common/net.rs:638
638     in library/std/src/sys_common/net.rs
(gdb) p $rip
$2 = (*mut fn ()) 0x558267510594 <std::net::udp::UdpSocket::recv+20>
(gdb) info symbol 0x558267510594
<std::net::tcp::TcpStream as std::io::Read>::read + 20 in section .text of /home/amos/bearcove/plaque/target/debug/plaque
(gdb)
```

Oh good. But wait, isn't this a debug build? Why would LLVM do that?

Well, our application is a debug build, but the standard lib is prebuilt (and optimized). Thanks to [Mara](https://twitter.com/m_ou_se) for helping me solve the puzzle.

Anyway! Let's pretend debugging is always ideal and that we're looking at this:

```
$ rust-gdb -quiet -pid $(pidof plaque) -ex "t a a bt" -ex "set confirm off" -ex "q" | 2>/dev/null | grep -A 90 'Thread 1' | grep -vE '[dD]etach(ing|ed)'
Thread 1 (Thread 0x7f7c481d7780 (LWP 775276) "plaque"):
#0  0x00007f7c482ed030 in __libc_recv (fd=4, buf=0x558267afeba0, len=1024, flags=0) at ../sysdeps/unix/sysv/linux/recv.c:28
#1  0x0000558267510594 in std::sys::unix::net::Socket::recv_with_flags () at library/std/src/sys/unix/net.rs:245
#2  std::sys::unix::net::Socket::read () at library/std/src/sys/unix/net.rs:251
#3  std::sys_common::net::TcpSocket::recv () at library/std/src/sys_common/net.rs:638
#4  std::net::tcp::TcpSocket::recv () at library/std/src/net/tcp.rs:whatever
#5  0x00005582674faf26 in plaque::main () at src/main.rs:19
```

That's the problem with blocking syscalls (which are roughly"function calls into the kernel", by the way) - we can only do one thing at a time. Here, we're either accepting new connections, or reading from an already-established connection, but never both at the same time.

We can solve this with more ~violence~ threads:

```
use std::{
    error::Error,
    io::{Read, Write},
    net::{SocketAddr, TcpListener, TcpStream},
};

fn main() -> Result<(), Box<dyn Error>> {
    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    let listener = TcpListener::bind(addr)?;
    println!("Listening on http://{}", addr);
    loop {
        let (stream, addr) = listener.accept()?;
        std::thread::spawn(move || {
            if let Err(e) = handle_connection(stream, addr) {
                println!("Error handling connection {addr}: {e}");
            }
        });
    }
}

fn handle_connection(mut stream: TcpStream, addr: SocketAddr) -> Result<(), Box<dyn Error>> {
    println!("Accepted connection from {addr}");

    let mut incoming = vec![];

    loop {
        let mut buf = vec![0u8; 1024];
        let read = stream.read(&mut buf)?;
        incoming.extend_from_slice(&buf[..read]);

        if incoming.len() > 4 && &incoming[incoming.len() - 4..] == b"\r\n\r\n" {
            break;
        }
    }

    let incoming = std::str::from_utf8(&incoming)?;
    println!("Got HTTP request:\n{}", incoming);
    stream.write_all(b"HTTP/1.1 200 OK\r\n")?;
    stream.write_all(b"\r\n")?;
    stream.write_all(b"Hello from plaque!\n")?;
    println!("Closing connection for {addr}");

    Ok(())
}
```

And now we can have _several_ threads stuck on a syscall:

```
$ rust-gdb -quiet -pid $(pidof plaque) -ex "t a a bt" -ex "set confirm off" -ex "q" | 2>/dev/null | grep -E -A 90 'Thread [0-9]*' | grep -vE '[dD]etach(ing|ed)'
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib64/libthread_db.so.1".
0x00007fd5eb1cd6f0 in accept4 (fd=3, addr=..., addr_len=0x7ffe2b2886fc, flags=524288) at ../sysdeps/unix/sysv/linux/accept4.c:32
32        return SYSCALL_CANCEL (accept4, fd, addr.__sockaddr__, addr_len, flags);

Thread 4 (Thread 0x7fd5eacb4640 (LWP 792836) "plaque"):
#0  __libc_recv (flags=<optimized out>, len=1024, buf=0x7fd5e0000c90, fd=6) at ../sysdeps/unix/sysv/linux/recv.c:28
(cut)
#20 0x00007fd5eb147b1a in start_thread (arg=<optimized out>) at pthread_create.c:443
#21 0x00007fd5eb1cc650 in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:81

Thread 3 (Thread 0x7fd5eaeb5640 (LWP 792671) "plaque"):
#0  __libc_recv (flags=<optimized out>, len=1024, buf=0x7fd5dc000c90, fd=5) at ../sysdeps/unix/sysv/linux/recv.c:28
(cut)
#20 0x00007fd5eb147b1a in start_thread (arg=<optimized out>) at pthread_create.c:443
#21 0x00007fd5eb1cc650 in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:81

Thread 2 (Thread 0x7fd5eb0b6640 (LWP 792521) "plaque"):
#0  __libc_recv (flags=<optimized out>, len=1024, buf=0x7fd5e4000c90, fd=4) at ../sysdeps/unix/sysv/linux/recv.c:28
(cut)
#20 0x00007fd5eb147b1a in start_thread (arg=<optimized out>) at pthread_create.c:443
#21 0x00007fd5eb1cc650 in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:81

Thread 1 (Thread 0x7fd5eb0b7780 (LWP 792264) "plaque"):
#0  0x00007fd5eb1cd6f0 in accept4 (fd=3, addr=..., addr_len=0x7ffe2b2886fc, flags=524288) at ../sysdeps/unix/sysv/linux/accept4.c:32
#1  0x000055d758e79de9 in std::sys::unix::net::{impl#0}::accept::{closure#0} () at library/std/src/sys/unix/net.rs:225
#2  std::sys::unix::cvt_r<i32, std::sys::unix::net::{impl#0}::accept::{closure#0}> () at library/std/src/sys/unix/mod.rs:212
#3  std::sys::unix::net::Socket::accept () at library/std/src/sys/unix/net.rs:225
#4  std::sys_common::net::TcpListener::accept () at library/std/src/sys_common/net.rs:407
#5  std::net::tcp::TcpListener::accept () at library/std/src/net/tcp.rs:811
#6  0x000055d758e5e0ec in plaque::main () at src/main.rs:12
```

Which is all well and good, until we start hitting some limits. Like, maybe we have SO MANY CONNECTIONS that we run out of memory, because each of these threads has its own stack, and that's not free. It's not _a lot_, but a lot of "not a lot" quickly becomes a lot, as we all learn sooner or later.

Luckily, there's a way to make those syscalls in a non-blocking manner: you tell them "I would like to please not block" and they sometimes reply immediately with a result, and other times with "well try again later, then".

But _when_ should you try again? Well, you can subscribe to events that let you know when a resource, say, a TCP socket, is ready to be read from, or written to.

And... that all sounds like a lot of bookkeeping. Wouldn't it be convenient if there was a system that took care of all that, and allowed you to code as if you were writing blocking code, but it would still be able to do multiple things concurrently with a single thread???

Well that's exactly what an async runtime is.

Enter tokio
-----------

So, let's make our program async! Well, let's make a simple async program and go from there.

```
$ cargo add tokio --features full
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tokio v1.17.0 to dependencies with features: ["full"]
```

Because I don't want you to think `tokio::main` is magic, let's first go without it:

```
use std::error::Error;

use tokio::net::TcpListener;

fn main() -> Result<(), Box<dyn Error>> {
    let rt = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()?;
    rt.block_on(async {
        let addr: SocketAddr = "0.0.0.0:3779".parse()?;
        println!("Listening on http://{}", addr);
        let listener = TcpListener::bind(addr).await?;
        loop {
            let (stream, addr) = listener.accept().await?;
            println!("Accepted connection from {addr}");
            // do nothing for now, it's a simple example
            drop(stream)
        }
    })
}
```

This accepts a connection and immediately closes it! I bet HTTP user agents (like curl and web browsers) won't be too happy about it.

```
# In terminal 1
$ cargo run --quiet
Listening on http://0.0.0.0:3779

# In terminal 2
$ curl http://0.0.0.0:3779
curl: (56) Recv failure: Connection reset by peer

# Meanwhile, in terminal 1
Accepted connection from 127.0.0.1:34620
```

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/its-edge-again.1fa576b36756f280.jpg) 

And as promised, we're not"blocked"on a syscall. Well... we're not blocked on `accept4`:

```
$ rust-gdb -quiet -pid $(pidof plaque) -ex "t a a bt" -ex "set confirm off" -ex "q" | 2>/dev/null | grep -E -A 90 'Thread [0-9]*' | grep -vE '[dD]etach(ing|ed)'
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib64/libthread_db.so.1".
0x00007f0f6b8cabea in epoll_wait (epfd=3, events=0x560ec6a4b410, maxevents=1024, timeout=-1) at ../sysdeps/unix/sysv/linux/epoll_wait.c:30
Downloading 0.00 MB source file /usr/src/debug/glibc-2.34-25.fc35.x86_64/misc/../sysdeps/unix/sysv/linux/epoll_wait.c...
30        return SYSCALL_CANCEL (epoll_wait, epfd, events, maxevents, timeout);

Thread 1 (Thread 0x7f0f6b7b7cc0 (LWP 1435153) "plaque"):
#0  0x00007f0f6b8cabea in epoll_wait (epfd=3, events=0x560ec6a4b410, maxevents=1024, timeout=-1) at ../sysdeps/unix/sysv/linux/epoll_wait.c:30
#1  0x0000560ec62f4c55 in mio::sys::unix::selector::epoll::Selector::select (self=0x7ffd9ab57950, events=0x7ffd9ab56ce0, timeout=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/mio-0.8.0/src/sys/unix/selector/epoll.rs:68
#2  0x0000560ec62fa1c7 in mio::poll::Poll::poll (self=0x7ffd9ab57950, events=0x7ffd9ab56ce0, timeout=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/mio-0.8.0/src/poll.rs:337
#3  0x0000560ec6276776 in tokio::io::driver::Driver::turn (self=0x7ffd9ab57770, max_wait=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/io/driver/mod.rs:163
#4  0x0000560ec62770df in tokio::io::driver::{impl#3}::park (self=0x7ffd9ab57770) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/io/driver/mod.rs:234
#5  0x0000560ec62a42ca in tokio::signal::unix::driver::{impl#1}::park (self=0x7ffd9ab57770) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/signal/unix/driver.rs:150
#6  0x0000560ec62bdaaa in tokio::process::imp::driver::{impl#1}::park (self=0x7ffd9ab57770) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/process/unix/driver.rs:44
#7  0x0000560ec627c363 in tokio::park::either::{impl#0}::park<tokio::process::imp::driver::Driver, tokio::park::thread::ParkThread> (self=0x7ffd9ab57768) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/park/either.rs:30
#8  0x0000560ec62a59a4 in tokio::time::driver::Driver<tokio::park::either::Either<tokio::process::imp::driver::Driver, tokio::park::thread::ParkThread>>::park_internal<tokio::park::either::Either<tokio::process::imp::driver::Driver, tokio::park::thread::ParkThread>> (self=0x7ffd9ab57740, limit=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/time/driver/mod.rs:238
#9  0x0000560ec62a5da0 in tokio::time::driver::{impl#3}::park<tokio::park::either::Either<tokio::process::imp::driver::Driver, tokio::park::thread::ParkThread>> (self=0x7ffd9ab57740) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/time/driver/mod.rs:436
#10 0x0000560ec627c44d in tokio::park::either::{impl#0}::park<tokio::time::driver::Driver<tokio::park::either::Either<tokio::process::imp::driver::Driver, tokio::park::thread::ParkThread>>, tokio::park::either::Either<tokio::process::imp::driver::Driver, tokio::park::thread::ParkThread>> (self=0x7ffd9ab57738) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/park/either.rs:30
#11 0x0000560ec623fa47 in tokio::runtime::driver::{impl#1}::park (self=0x7ffd9ab57738) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/driver.rs:198
#12 0x0000560ec623e047 in tokio::runtime::basic_scheduler::{impl#4}::park::{closure#1} () at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:315
#13 0x0000560ec623ea80 in tokio::runtime::basic_scheduler::Context::enter<(), tokio::runtime::basic_scheduler::{impl#4}::park::{closure#1}> (self=0x7ffd9ab58518, core=0x560ec6a522b0, f=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:356
#14 0x0000560ec623dd39 in tokio::runtime::basic_scheduler::Context::park (self=0x7ffd9ab58518, core=0x560ec6a522b0) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:314
#15 0x0000560ec622b0bf in tokio::runtime::basic_scheduler::{impl#9}::block_on::{closure#0}<core::pin::Pin<&mut core::future::from_generator::GenFuture<plaque::main::{generator#0}>>> (core=0x560ec6a522b0, context=0x7ffd9ab58518) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:522
#16 0x0000560ec622b8c2 in tokio::runtime::basic_scheduler::{impl#9}::enter::{closure#0}<tokio::runtime::basic_scheduler::{impl#9}::block_on::{closure#0}, core::result::Result<(), alloc::boxed::Box<dyn std::error::Error, alloc::alloc::Global>>> () at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:555
#17 0x0000560ec622e6c6 in tokio::macros::scoped_tls::ScopedKey<tokio::runtime::basic_scheduler::Context>::set<tokio::runtime::basic_scheduler::Context, tokio::runtime::basic_scheduler::{impl#9}::enter::{closure#0}, (alloc::boxed::Box<tokio::runtime::basic_scheduler::Core, alloc::alloc::Global>, core::result::Result<(), alloc::boxed::Box<dyn std::error::Error, alloc::alloc::Global>>)> (self=0x560ec63aca88 <tokio::runtime::basic_scheduler::CURRENT>, t=0x7ffd9ab58518, f=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/macros/scoped_tls.rs:61
#18 0x0000560ec622b648 in tokio::runtime::basic_scheduler::CoreGuard::enter<tokio::runtime::basic_scheduler::{impl#9}::block_on::{closure#0}, core::result::Result<(), alloc::boxed::Box<dyn std::error::Error, alloc::alloc::Global>>> (self=..., f=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:555
#19 0x0000560ec622aaf0 in tokio::runtime::basic_scheduler::CoreGuard::block_on<core::pin::Pin<&mut core::future::from_generator::GenFuture<plaque::main::{generator#0}>>> (self=..., future=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:488
#20 0x0000560ec6229de5 in tokio::runtime::basic_scheduler::BasicScheduler::block_on<core::future::from_generator::GenFuture<plaque::main::{generator#0}>> (self=0x7ffd9ab58b68, future=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:168
#21 0x0000560ec622eda3 in tokio::runtime::Runtime::block_on<core::future::from_generator::GenFuture<plaque::main::{generator#0}>> (self=0x7ffd9ab58b60, future=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/mod.rs:475
#22 0x0000560ec6232af4 in plaque::main () at src/main.rs:9
```

We can see the guts of the async runtime here. From bottom to top, we have our main function, our `block_on` invocation, some thread-local stuff ([this TLS](https://en.wikipedia.org/wiki/Thread-local_storage), not [that TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security)), we can see that the thread is "parked", which in this case means waiting for events coming out of "epoll", the mechanism that happens to be used by [tokio](https://lib.rs/crates/tokio) to perform I/O asynchronously on Linux.

Let's make the code shorter using the [#[tokio::main]](https://docs.rs/tokio/latest/tokio/attr.main.html) attribute macro:

```
use std::{error::Error, net::SocketAddr};

use tokio::net::TcpListener;

// 👇 this will take care of building the runtime
#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    // note: our function is now `async fn`

    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    println!("Listening on http://{}", addr);
    //                       we can await from there!  👇
    let listener = TcpListener::bind(addr).await?;
    loop {
        let (stream, addr) = listener.accept().await?;
        println!("Accepted connection from {addr}");
        // just do nothing, it's a simple example
        drop(stream)
    }
}
```

There! That's exactly equivalent to the longer version, just... more readable.

Now that we've convinced ourselves that `#[tokio::main]` is not too magic, let's keep porting our code to async Rust, via tokio:

```
use std::{error::Error, net::SocketAddr};

use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::TcpListener,
};

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    println!("Listening on http://{}", addr);
    let listener = TcpListener::bind(addr).await?;
    loop {
        let (mut stream, addr) = listener.accept().await?;
        println!("Accepted connection from {addr}");

        let mut incoming = vec![];

        loop {
            let mut buf = vec![0u8; 1024];
            let read = stream.read(&mut buf).await?;
            incoming.extend_from_slice(&buf[..read]);

            if incoming.len() > 4 && &incoming[incoming.len() - 4..] == b"\r\n\r\n" {
                break;
            }
        }

        let incoming = std::str::from_utf8(&incoming)?;
        println!("Got HTTP request:\n{}", incoming);
        stream.write_all(b"HTTP/1.1 200 OK\r\n").await?;
        stream.write_all(b"\r\n").await?;
        stream.write_all(b"Hello from plaque!\n").await?;
        println!("Closing connection for {addr}");
    }
}
```

There! It looks deceivingly like the sync version, there's just a bunch of `.await` sprinkled everywhere that might block: `bind`, `accept`, `read` and `write_all`.

Why `write_all`, by the way?

`write` doesn't have to write the whole buffer, that's why! `write_all` is a version that issues as many `write` as needed to write... all.

That seems peculiar... why is the interface designed that way?

Well, it's buffers all the way down. There might be room in the _kernel_'s TCP socket buffer for half of our buffer right now, and we may have to wait until it's drained, to write the rest.

Oh, that actually makes sense. I love it when things make sense!

So, that program behaves just like its sync counterpart, as in: it only handles one connection at a time. If client A connects, client B won't be able to connect until client A closes its connection (or has its connection closed by the server):

```
# In the server's terminal
$ cargo run --quiet
Listening on http://0.0.0.0:3779

# In client A's terminal
$ nc localhost 3779

# In the server's terminal
Accepted connection from 127.0.0.1:34696

# In client B's terminal
$ curl http://localhost:3779
```

But unlike the sync version of our code, it's not blocked on the `read` syscall. It's, again, blocked on `epoll_wait`:

```
$ rust-gdb -quiet -pid $(pidof plaque) -ex "t a a bt" -ex "set confirm off" -ex "q" | 2>/dev/null | grep -E -A 90 'Thread [0-9]*' | grep -vE '[dD]etach(ing|ed)'
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib64/libthread_db.so.1".
0x00007ff502a5fbea in epoll_wait (epfd=3, events=0x55ec9905b410, maxevents=1024, timeout=-1) at ../sysdeps/unix/sysv/linux/epoll_wait.c:30
30        return SYSCALL_CANCEL (epoll_wait, epfd, events, maxevents, timeout);

Thread 1 (Thread 0x7ff50294ccc0 (LWP 1441723) "plaque"):
#0  0x00007ff502a5fbea in epoll_wait (epfd=3, events=0x55ec9905b410, maxevents=1024, timeout=-1) at ../sysdeps/unix/sysv/linux/epoll_wait.c:30
#1  0x000055ec9871aef5 in mio::sys::unix::selector::epoll::Selector::select (self=0x7ffdc746ebf0, events=0x7ffdc746df80, timeout=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/mio-0.8.0/src/sys/unix/selector/epoll.rs:68
#2  0x000055ec987204c7 in mio::poll::Poll::poll (self=0x7ffdc746ebf0, events=0x7ffdc746df80, timeout=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/mio-0.8.0/src/poll.rs:337
#3  0x000055ec98699e66 in tokio::io::driver::Driver::turn (self=0x7ffdc746ea10, max_wait=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/io/driver/mod.rs:163
#4  0x000055ec9869a7cf in tokio::io::driver::{impl#3}::park (self=0x7ffdc746ea10) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/io/driver/mod.rs:234
(cut)
#21 0x000055ec9864d993 in tokio::runtime::Runtime::block_on<core::future::from_generator::GenFuture<plaque::main::{generator#0}>> (self=0x7ffdc74701f0, future=...) at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/mod.rs:475
#22 0x000055ec98651a8d in plaque::main () at src/main.rs:13
```

And so... from GDB, there's no great way to tell where it's stuck.

Async runtimes have, one way or another, their own stack traces to handle.

If we look at a somewhat equivalent Go program, for example:

```
package main

import (
	"fmt"
	"net"
	"strings"
)

func main() {
	addr := "0.0.0.0:3779"
	// the original example only listens on IPv4,
	listener, err := net.Listen("tcp4", addr)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Listening on http://%s\n", addr)

	for {
		conn, err := listener.Accept()
		if err != nil {
			panic(err)
		}
		fmt.Printf("Accepted connection from %v\n", conn.RemoteAddr())

		var incoming []byte
		for {
			buf := make([]byte, 1024)
			n, err := conn.Read(buf)
			if err != nil {
				panic(err)
			}

			incoming = append(incoming, buf[:n]...)

			if len(incoming) > 4 && strings.HasSuffix(string(incoming), "\r\n\r\n") {
				break
			}
		}

		// Go doesn't let us shadow bindings, let's use a scope to stay close to the
		// original example.
		{
			incoming := string(incoming)
			fmt.Printf("Got HTTP request:\n%s\n", incoming)
			conn.Write([]byte("HTTP/1.1 200 OK\r\n"))
			conn.Write([]byte("\r\n"))
			conn.Write([]byte("Hello from plaque!\n"))
			fmt.Printf("Closing connection for %v\n", conn.RemoteAddr())
			err = conn.Close()
			if err != nil {
				panic(err)
			}
		}
	}
}
```

It exhibits the exact same behavior: because we're not spawning a goroutine per connection, we can only service one connection at a time.

At startup, it's"blocked"on accepting connections, but we can't really see that from gdb _just by looking at threads_:

```
$ go build ./main.go
$ gdb --quiet --args ./main
Reading symbols from ./main...
Loading Go Runtime support.
(gdb) r
Starting program: /home/amos/bearcove/plaque/main 
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib64/libthread_db.so.1".
Listening on http://0.0.0.0:3779
^C
Thread 1 "main" received signal SIGINT, Interrupt.
runtime.epollwait () at /usr/local/go/src/runtime/sys_linux_amd64.s:666
666             MOVL    AX, ret+24(FP)
(gdb) t a a bt

Thread 5 (Thread 0x7fffcb7fe640 (LWP 1461205) "main"):
#0  runtime.futex () at /usr/local/go/src/runtime/sys_linux_amd64.s:520
#1  0x000000000042f196 in runtime.futexsleep (addr=0xfffffffffffffe00, val=0, ns=4598179) at /usr/local/go/src/runtime/os_linux.go:44
#2  0x000000000040bd27 in runtime.notesleep (n=0xfffffffffffffe00) at /usr/local/go/src/runtime/lock_futex.go:160
#3  0x00000000004398d1 in runtime.templateThread () at /usr/local/go/src/runtime/proc.go:2385
#4  0x0000000000438393 in runtime.mstart1 () at /usr/local/go/src/runtime/proc.go:1407
#5  0x00000000004382d9 in runtime.mstart0 () at /usr/local/go/src/runtime/proc.go:1365
#6  0x000000000045e925 in runtime.mstart () at /usr/local/go/src/runtime/asm_amd64.s:248
#7  0x0000000000463025 in runtime.mstart () at <autogenerated>:1
#8  0x000000000040181b in runtime/cgo(.text) ()
#9  0x0000000000000000 in ?? ()

(Threads 4 through 2 are parked, like Thread 5)

Thread 1 (Thread 0x7ffff7d9b740 (LWP 1461198) "main"):
#0  runtime.epollwait () at /usr/local/go/src/runtime/sys_linux_amd64.s:666
#1  0x000000000042eefc in runtime.netpoll (delay=<optimized out>) at /usr/local/go/src/runtime/netpoll_epoll.go:127
#2  0x000000000043abd3 in runtime.findrunnable () at /usr/local/go/src/runtime/proc.go:2947
#3  0x000000000043bdd9 in runtime.schedule () at /usr/local/go/src/runtime/proc.go:3367
#4  0x000000000043c32d in runtime.park_m (gp=0xc0000ce000) at /usr/local/go/src/runtime/proc.go:3516
#5  0x000000000045e9a3 in runtime.mcall () at /usr/local/go/src/runtime/asm_amd64.s:307
#6  0x0000000000463109 in runtime.newproc (siz=4581669, fn=0x45e8db <runtime.rt0_go+315>) at <autogenerated>:1
#7  0x0000000000000000 in ?? ()
(gdb)
```

All we can see _by looking at threads_ is that there's a thread blocking on `epollwait`.

As it turns out, there's GDB integration for the Go runtime (it ships with Go itself, see [this page](https://go.dev/doc/gdb) for more info), so we can also print the backtraces for goroutines:

```
(gdb) goroutine all backtrace
#0  runtime.gopark (unlockf=<optimized out>, lock=<optimized out>, reason=<optimized out>, traceEv=<optimized out>, traceskip=<optimized out>) at /usr/local/go/src/runtime/proc.go:367
#1  0x000000000042e613 in runtime.netpollblock (pd=<optimized out>, mode=<optimized out>, waitio=<optimized out>) at /usr/local/go/src/runtime/netpoll.go:454
#2  0x000000000045c4e9 in internal/poll.runtime_pollWait (pd=<optimized out>, mode=0) at /usr/local/go/src/runtime/netpoll.go:234
#3  0x000000000048b932 in internal/poll.(*pollDesc).wait (pd=<optimized out>, mode=0, isFile=192) at /usr/local/go/src/internal/poll/fd_poll_runtime.go:84
#4  0x000000000048cbac in internal/poll.(*pollDesc).waitRead (isFile=192, pd=<optimized out>) at /usr/local/go/src/internal/poll/fd_poll_runtime.go:89
#5  internal/poll.(*FD).Accept (fd=0xc0000d4000, ~r0=<optimized out>, ~r1=..., ~r2=..., ~r3=...) at /usr/local/go/src/internal/poll/fd_unix.go:402
#6  0x00000000004ae7b5 in net.(*netFD).accept (fd=0xc0000d4000) at /usr/local/go/src/net/fd_unix.go:173
#7  0x00000000004beb48 in net.(*TCPListener).accept (ln=0xc00000e048) at /usr/local/go/src/net/tcpsock_posix.go:140
#8  0x00000000004bdf5d in net.(*TCPListener).Accept (l=0xfffffffffffffffc) at /usr/local/go/src/net/tcpsock.go:262
#9  0x00000000004c5b18 in main.main () at /home/amos/bearcove/plaque/main.go:19
No such goroutine:  17
#0  runtime.gopark (unlockf=<optimized out>, lock=<optimized out>, reason=<optimized out>, traceEv=<optimized out>, traceskip=<optimized out>) at /usr/local/go/src/runtime/proc.go:367
#1  0x00000000004359ed in runtime.goparkunlock (reason=<optimized out>, traceEv=<optimized out>, traceskip=<optimized out>, lock=<optimized out>) at /usr/local/go/src/runtime/proc.go:372
#2  runtime.forcegchelper () at /usr/local/go/src/runtime/proc.go:306
#3  0x0000000000460be1 in runtime.goexit () at /usr/local/go/src/runtime/asm_amd64.s:1581
#4  0x0000000000000000 in ?? ()
(cut: three other parked goroutines)
```

And _here_ we can see where we're stuck on: `net.(*TCPListener).Accept`.

Can we get something similar for our Rust program?

Not really. At least, not yet.

As of early March 2022, here's what _I_ would do to help with that problem.

A bit of tracing
----------------

[tracing](https://lib.rs/crates/tracing) is a crate ecosystem that lets you... trace what's going on in your application. And it works for async code, too!

Right now, we've been using `println!` to log what's happening. Let's see what it would look like if we were using `tracing` instead:

```
$ cargo add tracing   
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tracing v0.1.31 to dependencies

$ cargo add tracing-subscriber --features env-filter
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tracing-subscriber v0.3.9 to dependencies with features: ["env-filter"]
```

```
use std::{error::Error, net::SocketAddr};

use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::TcpListener,
};
use tracing::{debug, info};

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    // 👇 this will print tracing events to standard output for humans to read
    tracing_subscriber::fmt::init();
    // (you can configure a bunch of options, but we're going all defaults for now)

    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    info!("Listening on http://{}", addr);
    let listener = TcpListener::bind(addr).await?;
    loop {
        let (mut stream, addr) = listener.accept().await?;
        info!(%addr, "Accepted connection");

        let mut incoming = vec![];

        loop {
            let mut buf = vec![0u8; 1024];
            let read = stream.read(&mut buf).await?;
            incoming.extend_from_slice(&buf[..read]);

            if incoming.len() > 4 && &incoming[incoming.len() - 4..] == b"\r\n\r\n" {
                break;
            }
        }

        let incoming = std::str::from_utf8(&incoming)?;
        debug!(%incoming, "Got HTTP request");
        stream.write_all(b"HTTP/1.1 200 OK\r\n").await?;
        stream.write_all(b"\r\n").await?;
        stream.write_all(b"Hello from plaque!\n").await?;
        info!(%addr, "Closing connection");
    }
}
```

By default, we get timestamps, log levels (which we can filter with the `RUST_LOG` environment variable - that's the `env-filter` feature we asked [cargo-edit](https://lib.rs/crates/cargo-edit) to enable earlier when we invoked `cargo add`), and neat formatting:

```
$ RUST_LOG=debug cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.01s
     Running `target/debug/plaque`
2022-03-03T17:22:22.837683Z  INFO plaque: Listening on http://0.0.0.0:3779
2022-03-03T17:22:24.077415Z  INFO plaque: Accepted connection addr=127.0.0.1:34718
2022-03-03T17:22:24.077511Z DEBUG plaque: Got HTTP request incoming=GET / HTTP/1.1
Host: localhost:3779
User-Agent: curl/7.79.1
Accept: */*


2022-03-03T17:22:24.077579Z  INFO plaque: Closing connection addr=127.0.0.1:34718
```

Also, colors!

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/tracing-subscriber-colors.56f8a2c79cfa8312.jpg) 

That's just scratching the surface though. Those are events, but we can also have spans: we could have a span for the whole server, another for accepting connections, another for our connection handler, one for accepting incoming connections, one for reading the incoming request and one for writing the response:

```
use std::{error::Error, net::SocketAddr};

use tokio::{
    io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt},
    net::{TcpListener, TcpStream},
};
use tracing::{debug, info, info_span, Instrument};

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    tracing_subscriber::fmt::init();

    run_server().await
}

// 👇 here we use an attribute macro
#[tracing::instrument]
async fn run_server() -> Result<(), Box<dyn Error>> {
    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    info!("Listening on http://{}", addr);
    let listener = TcpListener::bind(addr).await?;
    loop {
        //                      here we use a Future extension trait 👇
        let (stream, addr) = listener.accept().instrument(info_span!("accept")).await?;
        handle_connection(stream, addr).await?;
    }
}

#[tracing::instrument(skip(stream))]
async fn handle_connection(mut stream: TcpStream, addr: SocketAddr) -> Result<(), Box<dyn Error>> {
    let req = read_http_request(&mut stream).await?;
    debug!(%req, "Got HTTP request");
    write_http_response(&mut stream).await?;

    Ok(())
}

#[tracing::instrument(skip(stream))]
async fn read_http_request(mut stream: impl AsyncRead + Unpin) -> Result<String, Box<dyn Error>> {
    let mut incoming = vec![];

    loop {
        let mut buf = vec![0u8; 1024];
        let read = stream.read(&mut buf).await?;
        incoming.extend_from_slice(&buf[..read]);

        if incoming.len() > 4 && &incoming[incoming.len() - 4..] == b"\r\n\r\n" {
            break;
        }
    }

    Ok(String::from_utf8(incoming)?)
}

#[tracing::instrument(skip(stream))]
async fn write_http_response(mut stream: impl AsyncWrite + Unpin) -> Result<(), Box<dyn Error>> {
    stream.write_all(b"HTTP/1.1 200 OK\r\n").await?;
    stream.write_all(b"\r\n").await?;
    stream.write_all(b"Hello from plaque!\n").await?;
    Ok(())
}
```

```
$ RUST_LOG=debug cargo run
   Compiling plaque v0.1.0 (/home/amos/bearcove/plaque)
    Finished dev [unoptimized + debuginfo] target(s) in 1.19s
     Running `target/debug/plaque`
2022-03-03T17:47:10.565608Z  INFO run_server: plaque: Listening on http://0.0.0.0:3779
2022-03-03T17:47:11.203471Z DEBUG run_server:handle_connection{addr=127.0.0.1:34722}: plaque: Got HTTP request req=GET / HTTP/1.1
Host: localhost:3779
User-Agent: curl/7.79.1
Accept: */*
```

At first glance, there's not much of a difference... at least with the default `tracing-subscriber` formatter.

But let's try something like [tracing-tree](https://lib.rs/crates/tracing-tree):

```
$ cargo add tracing-tree
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tracing-tree v0.2.0 to dependencies
```

```
// omitted: other `use` directives

use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, Registry};
use tracing_tree::HierarchicalLayer;

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    // 👇 new!
    Registry::default()
        .with(EnvFilter::from_default_env())
        .with(
            HierarchicalLayer::new(2)
                .with_targets(true)
                .with_bracketed_fields(true),
        )
        .init();

    run_server().await
}
```

Now we get hierarchical output!

```
$ RUST_LOG=debug cargo run
   Compiling plaque v0.1.0 (/home/amos/bearcove/plaque)
    Finished dev [unoptimized + debuginfo] target(s) in 1.25s
     Running `target/debug/plaque`
plaque::run_server{}
  0ms  INFO plaque Listening on http://0.0.0.0:3779
  plaque::accept{}
  
  plaque::handle_connection{addr=127.0.0.1:34728}
    plaque::read_http_request{}
    
    0ms DEBUG plaque Got HTTP request, req=GET / HTTP/1.1
    Host: localhost:3779
    User-Agent: curl/7.79.1
    Accept: */*
    
    
    plaque::write_http_response{}
    
  
  plaque::accept{}
```

Here it is with colors:

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/tracing-tree.99c7b4a8b0c8d6be.jpg) 

I love `tracing-tree` because it shows not only events, but also when we enter/exit spans. There's [a bunch of knobs you can turn](https://docs.rs/tracing-tree/0.2.0/tracing_tree/struct.HierarchicalLayer.html) to get the output juuuuust right.

And that means... we can kinda see where we get "stuck"! Here we can see it's in"accept".

Of course that's definitely not the same as a debugger: if there were other tasks running in our async runtime, we wouldn't see them. We're not able to list all the tasks, see their full backtrace, etc.

Here's another thing we can do with tracing: it's all structured, so instead of printing human-readable, we can print newline-delimited JSON! And because it's all composable, we can use that at the same time as tracing-tree: just add a layer!

```
$ cargo add tracing-subscriber --features "env-filter json"
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tracing-subscriber v0.3.9 to dependencies with features: ["env-filter", "json"]
```

```
#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    Registry::default()
        .with(EnvFilter::from_default_env())
        .with(
            HierarchicalLayer::new(2)
                .with_targets(true)
                .with_bracketed_fields(true),
        )
        // 👇 new!
        .with(
            tracing_subscriber::fmt::layer()
                .json()
                .with_writer(|| File::create("/tmp/log.json").unwrap()),
        )
        .init();

    run_server().await
}
```

Here's a request from Chrome logged as JSON, for example:

```
{
  "timestamp": "2022-03-03T18:11:04.867737Z",
  "level": "DEBUG",
  "fields": {
    "message": "Got HTTP request",
    "req": "GET /favicon.ico HTTP/1.1\r\nHost: localhost:3779\r\nConnection: keep-alive\r\nsec-ch-ua: \" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"\r\nDNT: 1\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nsec-ch-ua-platform: \"Windows\"\r\nAccept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: no-cors\r\nSec-Fetch-Dest: image\r\nReferer: http://localhost:3779/\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,de;q=0.6\r\nCookie: admin=\r\n\r\n"
  },
  "target": "plaque",
  "span": {
    "addr": "127.0.0.1:34734",
    "name": "handle_connection"
  },
  "spans": [
    {
      "name": "run_server"
    },
    {
      "addr": "127.0.0.1:34734",
      "name": "handle_connection"
    }
  ]
}
```

But let's dream bigger. Let's dream _better_.

It's easy to imagine that, given the examples we've seen, we have enough information about spans and traces to be able to send them, in a structured way, to various tools and services to allow us to dig even deeper into them.

For example, we could generate a Chrome trace out of it:

```
$ cargo add tracing-chrome
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tracing-chrome v0.4.0 to dependencies
```

```
#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    let (chrome_layer, _guard) = tracing_chrome::ChromeLayerBuilder::new()
        .file("/shared/chrome-trace.json".into())
        .build();
    Registry::default()
        .with(EnvFilter::from_default_env())
        .with(
            HierarchicalLayer::new(2)
                .with_targets(true)
                .with_bracketed_fields(true),
        )
        .with(chrome_layer)
        .init();

    run_server().await
}
```

And visualize it from Chrome:

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/tracing-chrome.61ea5d352908b1f8.jpg) 

Which is not even the best visualizer for these btw: there's a lot of tools out there that process this format, like [Perfetto](https://ui.perfetto.dev/) and [Speedscope](https://www.speedscope.app/).

The Chrome tracing format isn't the best fit for what we're after though (which is figuring out what's happening in our async app): we might want to look at a number of [OpenTelemetry](https://opentelemetry.io/) collectors.

We could go for [Honeycomb](https://www.honeycomb.io/), [Datadog](https://www.datadoghq.com/), and many others. Heck, even [Sentry](https://sentry.io/welcome/) accepts traces now.

Because I'm always trying to make my articles"do-try-this-at-home", we'll go with something self-hosted here: [Jaeger](https://www.jaegertracing.io/download/).

Because of the OpenTelemetry indirection, the setup is a tad more involved, but it's just that: setup. The code remains the same, and is instrumented the same way.

```
$ cargo add opentelemetry --features rt-tokio
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding opentelemetry v0.17.0 to dependencies with features: ["rt-tokio"]

$ cargo add opentelemetry-jaeger --features rt-tokio
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding opentelemetry-jaeger v0.16.0 to dependencies with features: ["rt-tokio"]

$ cargo add tracing-opentelemetry
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tracing-opentelemetry v0.17.2 to dependencies
```

```
#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    let tracer =
        opentelemetry_jaeger::new_pipeline().install_batch(opentelemetry::runtime::Tokio)?;

    let telemetry = tracing_opentelemetry::layer().with_tracer(tracer);

    Registry::default()
        .with(EnvFilter::from_default_env())
        .with(
            HierarchicalLayer::new(2)
                .with_targets(true)
                .with_bracketed_fields(true),
        )
        .with(telemetry)
        .init();

    run_server().await?;

    opentelemetry::global::shutdown_tracer_provider();

    Ok(())
}
```

Hey that wasn't even half bad!

Now let's start Jaeger in the background, as a container:

```
$ docker run -d -p6831:6831/udp -p6832:6832/udp -p16686:16686 -p14268:14268 jaegertracing/all-in-one:latest
```

Huh. No output? Is it even running?

```
$ docker ps
CONTAINER ID   IMAGE                             COMMAND                  CREATED              STATUS              PORTS                                                                                                                                                                                        NAMES
3b0727ba7f92   jaegertracing/all-in-one:latest   "/go/bin/all-in-one-…"   About a minute ago   Up About a minute   5778/tcp, 0.0.0.0:14268->14268/tcp, :::14268->14268/tcp, 5775/udp, 14250/tcp, 0.0.0.0:6831-6832->6831-6832/udp, :::6831-6832->6831-6832/udp, 0.0.0.0:16686->16686/tcp, :::16686->16686/tcp   crazy_volhard
```

The Jaeger "all-in-one" container is serving its web UI on [http://localhost:16686](http://localhost:16686/):

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/jaeger-empty.56abbdb41c91d47a.jpg) 

If we run our server and hit it with curl, then refresh Jaeger, we can see that it received traces from two services: `jaeger-query` (jaeger instruments itself!), and `unknown_service`: we haven't really done any configuration at all, and OpenTelemetry accepts extra metadata compared to tracing, so we're gonna see a bunch of default values here.

Clicking "Search" shows the traces we've received so far:

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/jaeger-unknown-service.bf45e1ded39990bc.jpg) 

Clicking on a trace shows an expanded view, with all the associated spans:

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/jaeger-trace.e0fab4e1bf8a26a5.jpg) 

And notice that the attributes we've set are there: they're called "tags" here. `accept_connection` has the `addr`. The "Got HTTP request" event has the full HTTP request header associated to it.

Because we have a top-level span, _all requests_ are actually grouped together: if we run several requests, we can see that they all have a parent in common, and we can see us "spending time" in accept (in scare quotes because again, the thread is actually parked, and so it's mostly idle - mostly because there's background tasks now, flushing traces and whatnot).

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/jaeger-many-traces.b78aa273a2bfdd0b.jpg) 

If we remove some spans, by removing the `#[tracing::instrument]` attribute on `run_server`, each connection has its own trace:

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/jaeger-no-toplevel.e66c14313edc2a71.jpg) 

On top of all traces, there's a graph that shows latency for the `handle_connection` "operation": it's between 500 and 600 microseconds.

That's on a debug build. If I do `RUST_LOG=debug cargo run --release` instead, I see latencies of around 150 microseconds instead.

There would be a lot more to say about OpenTelemetry, but for now, let's skip to the last tool we'll see before addressing the topic at hand: [tokio-console](https://lib.rs/crates/tokio-console).

```
$ cargo install tokio-console
    Updating crates.io index
     Ignored package `tokio-console v0.1.2` is already installed, use --force to override
```

It gives us a dynamic realtime view into what's going on within a Tokio runtime: it's less GDB and more [top(1)](https://linux.die.net/man/1/top).

Unfortunately, for performance reasons, we can't really use that on a production app, but since we're playing around locally, there's nothing stopping us.

The full instructions to enable it are [in tokio-console's documentation](https://lib.rs/crates/tokio-console): I won't reproduce them here because `tokio-console` is still in the early stages and I expect the instructions to change.

At the time of this writing, `tokio-console` relies on [console-subscriber](https://lib.rs/crates/console-subscriber), which is, you guessed it, a `tracing` layer!

So, we can just add it to the pile:

```
#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    let tracer =
        opentelemetry_jaeger::new_pipeline().install_batch(opentelemetry::runtime::Tokio)?;

    let telemetry = tracing_opentelemetry::layer().with_tracer(tracer);

    let (console, server) = console_subscriber::ConsoleLayer::builder().build();
    tokio::spawn(async move {
        server.serve().await.unwrap();
    });

    Registry::default()
        .with(EnvFilter::from_default_env())
        .with(
            HierarchicalLayer::new(2)
                .with_targets(true)
                .with_bracketed_fields(true),
        )
        .with(telemetry)
        .with(console)
        .init();

    run_server().await?;

    opentelemetry::global::shutdown_tracer_provider();

    Ok(())
}
```

_There's other steps I'm not showing: several features to enable, via `Cargo.toml`, also `.cargo/config.toml`. Read the docs!_

The instructions I'm reading now state that we must have `tokio=trace,runtime=trace` in our env filter, so, that's how we want to start the app in order to let `console-subscriber` work:

```
$ RUST_LOG=tokio=trace,runtime=trace,debug cargo run
```

And now, after starting our application, we can run `tokio-console`.

By default, it opens on the tasks view:

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/tokio-console-tasks.06d19126d60ee038.jpg) 

We can see two of console-subscriber's internal tasks, and two hyper tasks. We can scroll through tasks with the up and down arrows (or k and j, for the [vi-inclined](https://en.wikipedia.org/wiki/Arrow_keys#HJKL_keys)), and pressing enter shows details for a task...

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/tokio-console-single-task.2be63f0e6338bca2.jpg) 

...including its name, target, the location in code where it was spawned, how long it's existed, and how much CPU time we've spent on it. There's also statistics about its wakers (think about asynchronous I/O operations on TCP sockets again: we need to have a way to wake up a task when the socket is ready to be read from/written to), and a wonderful poll time histogram, along with percentiles: we can see it's usually done in under 5 milliseconds (that's a debug build again).

Unfortunately, for now:

*   There's no stack trace (unsurprising, stack traces are not recorded)
*   There's no _span trace_ either: we don't know the context in which this was spanned
*   The only API to set the name of a task is internal and behind feature flags
*   I have no idea how fields are set: I have never seen a field other than "kind=task"

I see those as hints of what's planned for `tokio-console` - and I can't wait to see more!

Let's take a quick look at the"resources" view as well:

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/tokio-console-resources.27d84e738032dfcc.jpg) 

This is a recent improvement: timers are only tracked since tokio 1.13.0, and mutexes / rwlocks / channels are only tracked since tokio 1.15.0.

Just looking at this, I'm guessing that our"batched" opentelemetry span exporter exports... every thirty seconds! Since it seems to be sleeping for 30 seconds.

I have no idea what all those semaphores are used for, it seems like `console-subscriber` is doing things at an interval (probably sending data to `tokio-console`), and it seems tokio's intervals are implemented in terms of `sleep`, if the last line is to be believed.

Like for tasks, scrolling to a specific resource and pressing enter shows us a detail view: for the interval, we can see a list of async ops:

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/tokio-console-async-ops.2e83527357c5ab3f.jpg) 

Which is neat, because it means the relationship between resources and tasks is already being tracked. Again, there's a lot planned for tokio-console, you can check out [its repository](https://github.com/tokio-rs/console/) to keep track of what's happening.

I can't help but notice there's nothing in there about us accepting connections... right?

Ah, right... well it's not spawned as a task, maybe if we spawn it as a task?

```
#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    // omitted: tracing + opentelemetry setup

    let handle = tokio::task::spawn(async { run_server().await.unwrap() });
    handle.await?;

    opentelemetry::global::shutdown_tracer_provider();

    Ok(())
}
```

If we do that, then yes indeed, our task does show up! It has an empty name, but the `location` is right: it's in `main.rs` somewhere.

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/tokio-console-main-task.61b61670f89ed25f.jpg) 

And we can see from the poll time histogram that we're spending around 100 microseconds to 260 microseconds polling it: this is not the same as latency, because it might need to be polled multiple times for a single HTTP request to be handled, since it involves an accept, one or more reads, and multiple writes.

Looking at thread backtraces isn't too useful when we're using an async runtime. This is true of Go, too, but they track enough information about goroutines and have added enough support to GDB that you can list all goroutine backtraces (also via [pprof](https://pkg.go.dev/net/http/pprof) over HTTP), and that's invaluable.

In Rust, with the tokio runtime, there is no such thing - yet. That's typically something the [Async workgroup](https://rust-lang.github.io/wg-async/index.html) would be working on.

However, we've discovered the [tracing ecosystem](https://lib.rs/keywords/tracing), which makes it extremely easy to collect structured spans and events and send them to various places: as human-readable logs, JSON lines, profiler dumps, any OpenTelemetry tracing solution, etc.

Crates like [color-eyre](https://lib.rs/crates/color-eyre), although not shown here, also integrate nicely into the tracing ecosystem, showing not only stacktraces, but also spantraces.

[tokio-console](https://lib.rs/crates/tokio-console) brands itself "top(1) for tokio", and although it's not usable in production yet, there are many exciting plans around it, notably around answering questions like "why is this task not making progress? what resources does it depend on?". There's still a lot of open questions about the exact design of the plumbing around all of this.

Before we move on beyond TCP APIs to a proper HTTP framework, let's just make a version of our async program that can actually service multiple clients in parallel, just for comparison with the sync version.

```
// omitted: everything else (which stays the same)

async fn run_server() -> Result<(), Box<dyn Error>> {
    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    info!("Listening on http://{}", addr);
    let listener = TcpListener::bind(addr).await?;
    loop {
        let (stream, addr) = listener.accept().instrument(info_span!("accept")).await?;
        tokio::spawn(async move {
            if let Err(err) = handle_connection(stream, addr).await {
                error!(%err, "Error handling connection" );
            }
        });
    }
}
```

It's very similar, except it uses `tokio::spawn` rather than `std::thread::spawn`. Just like we can move resources (a `TcpStream` and a `SocketAddr`) into threads, we can move then into futures (which are then spawned as tasks on a runtime, so that they get polled in the background).

I couldn't resist running [oha](https://lib.rs/crates/oha) against a release build of this program: the numbers are completely meaningless and should be ignored, but look at the nice TUI (text user interface):

 ![](https://fasterthanli.me/content/articles/request-coalescing-in-async-rust/assets/oha-tcp.bcb0150a81a50afb.jpg) 

oha's final report (again, just for show, this is all very unscientific and zero effort went into making this fair or meaningful) reads:

```
$ oha -z 10s http://localhost:3779
Summary:
  Success rate: 1.0000
  Total:        10.0003 secs
  Slowest:      0.0135 secs
  Fastest:      0.0002 secs
  Average:      0.0011 secs
  Requests/sec: 46809.3602

  Total data:   8.48 MiB
  Size/request: 19 B
  Size/sec:     868.53 KiB

Response time histogram:
  0.000 [201]    |
  0.001 [1204]   |
  0.001 [277131] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.001 [167022] |■■■■■■■■■■■■■■■■■■■
  0.001 [12561]  |■
  0.002 [3754]   |
  0.002 [1728]   |
  0.002 [1146]   |
  0.002 [927]    |
  0.003 [333]    |
  0.003 [2101]   |

Latency distribution:
  10% in 0.0009 secs
  25% in 0.0010 secs
  50% in 0.0010 secs
  75% in 0.0011 secs
  90% in 0.0012 secs
  95% in 0.0013 secs
  99% in 0.0021 secs

Details (average, fastest, slowest):
  DNS+dialup:   0.0001 secs, 0.0000 secs, 0.0114 secs
  DNS-lookup:   0.0000 secs, 0.0000 secs, 0.0059 secs

Status code distribution:
  [200] 468108 responses
```

And now, a proper http framework
--------------------------------

So we've had our fun, implementing HTTP by hand - a tiny tiny fraction of it, incorrectly, with terrible buffering hygiene, etc. It allowed us to compare synchronous and asynchronous code, talk about why async code is hard to debug in general, and discover the tracing ecosystem.

All of this comes in handy... right now!

Let's change our server application to use [axum](https://lib.rs/crates/axum) instead. It's built on top of [hyper](https://lib.rs/crates/hyper), which powers [fly.io](https://fly.io/)'s edge network, among many other things.

```
$ cargo add axum
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding axum v0.4.8 to dependencies
```

We'll keep all our tracing setup intact, in a module:

```
// in `src/tracing_stuff.rs`

use std::error::Error;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter, Registry};
use tracing_tree::HierarchicalLayer;

pub(crate) fn setup() -> Result<(), Box<dyn Error>> {
    let tracer =
        opentelemetry_jaeger::new_pipeline().install_batch(opentelemetry::runtime::Tokio)?;
    let telemetry = tracing_opentelemetry::layer().with_tracer(tracer);
    Registry::default()
        .with(EnvFilter::from_default_env())
        .with(
            HierarchicalLayer::new(2)
                .with_targets(true)
                .with_bracketed_fields(true),
        )
        .with(telemetry)
        .init();

    Ok(())
}

pub(crate) fn teardown() {
    opentelemetry::global::shutdown_tracer_provider();
}
```

...and write the simplest axum app that behaves exactly like our cobbled-together HTTP server did:

```
// in `src/main.rs`

use std::{error::Error, net::SocketAddr};

use axum::{response::IntoResponse, routing::get, Router, Server};
use tracing::info;

mod tracing_stuff;

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    tracing_stuff::setup()?;
    run_server().await?;
    tracing_stuff::teardown();
    Ok(())
}

async fn run_server() -> Result<(), Box<dyn Error>> {
    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    info!("Listening on http://{}", addr);

    let app = Router::new().route("/", get(root));
    Server::bind(&addr).serve(app.into_make_service()).await?;

    Ok(())
}

#[tracing::instrument]
async fn root() -> impl IntoResponse {
    "Hello from plaque!\n"
}
```

Well, I like the looks of that.

Right??? I've been waiting for something like `axum` forever.

It works fine in curl:

```
curl -v http://localhost:3779
*   Trying 127.0.0.1:3779...
* Connected to localhost (127.0.0.1) port 3779 (#0)
> GET / HTTP/1.1
> Host: localhost:3779
> User-Agent: curl/7.79.1
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< content-type: text/plain; charset=utf-8
< content-length: 19
< date: Thu, 03 Mar 2022 20:44:39 GMT
< 
Hello from plaque!
* Connection #0 to host localhost left intact
```

...and, you know, it actually sends some useful response headers.

Predictably, it also works fine in a proper web browser, and... I couldn't resist running [oha](https://lib.rs/crates/oha) on it as well:

```
(results shortened)

Response time histogram:
  0.000 [430]     |
  0.000 [3277]    |
  0.000 [233959]  |■■■■■■
  0.000 [1074275] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.000 [123655]  |■■■
  0.001 [7550]    |
  0.001 [1951]    |
  0.001 [1155]    |
  0.001 [519]     |
  0.001 [177]     |
  0.001 [7737]    |

Latency distribution:
  10% in 0.0003 secs
  25% in 0.0003 secs
  50% in 0.0003 secs
  75% in 0.0004 secs
  90% in 0.0004 secs
  95% in 0.0004 secs
  99% in 0.0005 secs
```

Wait... 4? Didn't our latency numbers end in 1 earlier?

Yeah. 0.001 vs 0.0004 seconds.

So, now that we've reassured ourselves performance-wise, let's take a look at tracing!

We still have `tracing-tree` set up and everything, and we've instrumented the `root` async function, but it doesn't have a lot of information:

```
$ RUST_LOG=info cargo run --release
    Finished release [optimized] target(s) in 0.03s
     Running `target/release/plaque`
 INFO plaque Listening on http://0.0.0.0:3779
plaque::root{}

plaque::root{}

plaque::root{}

plaque::root{}
```

...because a lot of things are handled by `hyper` and `axum` now.

But what's cool is that `hyper` taps into the `tower` ecosystem, which is made of composable layers, much like `tracing`!

So if we pull in `tower-http`, we can add some tracing easily:

```
$ cargo add tower
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tower v0.4.12 to dependencies

$ cargo add tower-http --features trace
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tower-http v0.2.3 to dependencies with features: ["trace"]
```

```
async fn run_server() -> Result<(), Box<dyn Error>> {
    let addr: SocketAddr = "0.0.0.0:3779".parse()?;
    info!("Listening on http://{}", addr);

    let app = Router::new().route("/", get(root)).layer(
        ServiceBuilder::new()
            // 👇 new!
            .layer(TraceLayer::new_for_http())
            .into_inner(),
    );
    Server::bind(&addr).serve(app.into_make_service()).await?;

    Ok(())
}
```

There's a wealth of middleware to pick from, that's just one of them!

And now, our server emits events whenever it serves a request:

```
$ RUST_LOG=tower_http=debug cargo run --release
    Finished release [optimized] target(s) in 0.03s
     Running `target/release/plaque`
tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  0ms DEBUG tower_http::trace::on_response finished processing request, latency=0 ms, status=200

tower_http::trace::make_span::request{method=GET, uri=/uh-oh, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  0ms DEBUG tower_http::trace::on_response finished processing request, latency=0 ms, status=404
```

...no matter whether it serves it over plaintext HTTP/1, HTTPS, HTTP/2, etc.

We'd probably want to roll our own layer if we needed something a little more detailed: and we'd have all the required integration points to do so.

A useful http service
---------------------

And now, to move beyond the hello world.

Let's make an HTTP request handler that returns the ID of the latest video on [my YouTube channel](https://www.youtube.com/c/fasterthanlime).

I picked this example because:

*   It can be done using the public YouTube API: no API key required!
*   I'm somewhat scared of being rate-limited when doing this

Because of potential rate-limiting going on, that's one of the first things I deduplicated/memoized/single-flighted/cached in my site (not counting static content).

So! We'll be using the [https://www.youtube.com/feeds/videos.xml](https://www.youtube.com/feeds/videos.xml) API endpoint. It accepts a `channel_id` query parameter, and my channel ID is `UCs4fQRyl1TJvoeOdekW6lYA`.

We'll make all of that happen in a separate module named `youtube`:

```
// in `src/main.rs`

mod youtube;
```

First we'll want to build the URL. And I don't feel like doing string interpolation right now - I want only your strongest types, potion seller[.](https://www.youtube.com/watch?v=R_FQU4KzN7A&t=2s)

```
$ cargo add url
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding url v2.2.2 to dependencie
```

Ok, let's build!

```
// in `src/youtube.rs`

use std::error::Error;
use url::Url;

const YT_CHANNEL_ID: &str = "UCs4fQRyl1TJvoeOdekW6lYA";

#[tracing::instrument]
pub(crate) async fn fetch_video_id() -> Result<String, Box<dyn Error>> {
    let mut api_url = Url::parse("https://www.youtube.com/feeds/videos.xml")?;
    {
        let mut q = api_url.query_pairs_mut();
        q.append_pair("channel_id", YT_CHANNEL_ID);
    }

    todo!("fetch from {api_url}");
}
```

And we'll change our `root` endpoint to call it...

```
// in `src/main.rs`

#[tracing::instrument]
async fn root() -> impl IntoResponse {
    youtube::fetch_video_id().await.unwrap()
}
```

```
$ RUST_LOG=tower_http=debug cargo run --release
    Finished release [optimized] target(s) in 0.03s
     Running `target/release/plaque`
tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
thread 'main' panicked at 'not yet implemented: fetch from https://www.youtube.com/feeds/videos.xml?channel_id=UCs4fQRyl1TJvoeOdekW6lYA', src/youtube.rs:13:5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

Okay! URL looks good (I checked by opening it in a browser).

I'm not super happy with the error handling though - making the whole task panic seems a little heavy-handed.

It also feels like the perfect time to showcase [color-eyre](https://lib.rs/crates/color-eyre).

```
$ cargo add color-eyre 
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding color-eyre v0.6.1 to dependencies
```

To get spantrace capture to work, we'll also need to install a [tracing-error](https://lib.rs/crates/tracing-error) layer:

```
$ cargo add tracing-error
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tracing-error v0.2.0 to dependencies
```

```
// in `src/tracing_stuff.rs`

use tracing_error::ErrorLayer;

// in the `setup` function,
// deep in the `.with` chain:

    Registry::default()
        .with(EnvFilter::from_default_env())
        .with(
            HierarchicalLayer::new(2)
                .with_targets(true)
                .with_bracketed_fields(true),
        )
        // 👇 there!
        .with(ErrorLayer::default())
        .with(telemetry)
        .init();
```

And now, we install `color_eyre` as the default panic handler, in `main`:

```
// in `src/main.rs`

// (omitted: everything else)

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn Error>> {
    color_eyre::install()?;

    tracing_stuff::setup()?;
    run_server().await?;
    tracing_stuff::teardown();
    Ok(())
}
```

```
$ RUST_LOG=tower_http=debug,info cargo run --release
    Finished release [optimized] target(s) in 0.03s
     Running `target/release/plaque`
 INFO plaque Listening on http://0.0.0.0:3779
tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  plaque::root{}
    plaque::youtube::fetch_video_id{}
The application panicked (crashed).
Message:  not yet implemented: fetch from https://www.youtube.com/feeds/videos.xml?channel_id=UCs4fQRyl1TJvoeOdekW6lYA
Location: src/youtube.rs:14

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SPANTRACE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   0: plaque::youtube::fetch_video_id
      at src/youtube.rs:6
   1: plaque::root
      at src/main.rs:35
   2: tower_http::trace::make_span::request with method=GET uri=/ version=HTTP/1.1
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/trace/make_span.rs:116

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
```

Well, isn't that delightful!

In case you're _not_ following along at home, let's see what the thread backtrace looks like. Because I'm running a release build here (I'm passing `--release` to cargo), let's make sure just enough debug information is included so that we get source file / line numbers info in our stacktrace:

```
# in `Cargo.toml`

# omitted: everything else ([package], [dependencies], etc.)

[profile.release]
# 2/true is too much, 0 is not enough, 1 is just right for backtraces
debug = 1
```

And now:

```
$ RUST_BACKTRACE=1 cargo run --release
Finished release [optimized + debuginfo] target(s) in 0.03s
     Running `target/release/plaque`
 INFO plaque Listening on http://0.0.0.0:3779
tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  plaque::root{}
    plaque::youtube::fetch_video_id{}
The application panicked (crashed).
Message:  not yet implemented: fetch from https://www.youtube.com/feeds/videos.xml?channel_id=UCs4fQRyl1TJvoeOdekW6lYA
Location: src/youtube.rs:14

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SPANTRACE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   0: plaque::youtube::fetch_video_id
      at src/youtube.rs:6
   1: plaque::root
      at src/main.rs:35
   2: tower_http::trace::make_span::request with method=GET uri=/ version=HTTP/1.1
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/trace/make_span.rs:116

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ BACKTRACE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                ⋮ 7 frames hidden ⋮                               
   8: plaque::youtube::fetch_video_id::{{closure}}::{{closure}}::hab8f271bc61b75d4
      at /home/amos/bearcove/plaque/src/youtube.rs:14
   9: <core::future::from_generator::GenFuture<T> as core::future::future::Future>::poll::h6e0e23eb00ce4823
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/future/mod.rs:84
  10: <tracing::instrument::Instrumented<T> as core::future::future::Future>::poll::h0be1db02d1392ae8
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tracing-0.1.31/src/instrument.rs:272
  11: plaque::youtube::fetch_video_id::{{closure}}::hf6d51b72f3f19269
      at /home/amos/bearcove/plaque/src/youtube.rs:6
  12: <core::future::from_generator::GenFuture<T> as core::future::future::Future>::poll::h6cb6341d279017f6
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/future/mod.rs:84
  13: plaque::root::{{closure}}::{{closure}}::h630b187fb3cddb8a
      at /home/amos/bearcove/plaque/src/main.rs:37
  14: <core::future::from_generator::GenFuture<T> as core::future::future::Future>::poll::h6ddf6f485ebbd74f
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/future/mod.rs:84
  15: <tracing::instrument::Instrumented<T> as core::future::future::Future>::poll::h0b761b74342ffab4
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tracing-0.1.31/src/instrument.rs:272
  16: plaque::root::{{closure}}::hf30871c07e78c6fd
      at /home/amos/bearcove/plaque/src/main.rs:35
  17: <core::future::from_generator::GenFuture<T> as core::future::future::Future>::poll::hc5fc9ae1f1172d28
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/future/mod.rs:84
  18: <F as axum::handler::Handler<(),B>>::call::{{closure}}::h4b190ad50776c570
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/axum-0.4.8/src/handler/mod.rs:274
  19: <core::future::from_generator::GenFuture<T> as core::future::future::Future>::poll::hd4c31eb92d321c5c
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/future/mod.rs:84
  20: <core::pin::Pin<P> as core::future::future::Future>::poll::h194730287d082d5b
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/future/future.rs:123
  21: <futures_util::future::future::map::Map<Fut,F> as core::future::future::Future>::poll::hda5093c773501670
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/futures-util-0.3.21/src/future/future/map.rs:55
  22: <futures_util::future::future::Map<Fut,F> as core::future::future::Future>::poll::h35098e19f97e2dfa
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/futures-util-0.3.21/src/lib.rs:91
  23: <axum::handler::future::IntoServiceFuture as core::future::future::Future>::poll::h83968b7e939194bc
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/axum-0.4.8/src/macros.rs:42
  24: <core::pin::Pin<P> as core::future::future::Future>::poll::h1d3bccc0ccc1322c
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/future/future.rs:123
  25: <tower::util::oneshot::Oneshot<S,Req> as core::future::future::Future>::poll::ha7c9f6e93564c479
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-0.4.12/src/util/oneshot.rs:97
  26: <axum::routing::route::RouteFuture<B,E> as core::future::future::Future>::poll::he8321bd83c70eaf0
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/axum-0.4.8/src/routing/route.rs:108
  27: <tower_http::trace::future::ResponseFuture<Fut,C,OnResponseT,OnBodyChunkT,OnEosT,OnFailureT> as core::future::future::Future>::poll::h146cd7d5d1401fa8
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/trace/future.rs:52
  28: <tower_http::map_response_body::ResponseFuture<Fut,F> as core::future::future::Future>::poll::h052add6c17b2403c
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/map_response_body.rs:204
  29: <tower_http::map_response_body::ResponseFuture<Fut,F> as core::future::future::Future>::poll::hf0cd011d85831398
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/map_response_body.rs:204
  30: <core::pin::Pin<P> as core::future::future::Future>::poll::h1d3bccc0ccc1322c
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/future/future.rs:123
  31: <tower::util::oneshot::Oneshot<S,Req> as core::future::future::Future>::poll::ha7c9f6e93564c479
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-0.4.12/src/util/oneshot.rs:97
  32: <axum::routing::route::RouteFuture<B,E> as core::future::future::Future>::poll::he8321bd83c70eaf0
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/axum-0.4.8/src/routing/route.rs:108
  33: <futures_util::future::either::Either<A,B> as core::future::future::Future>::poll::h5c1aa3799a3a97a8
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/futures-util-0.3.21/src/future/either.rs:89
  34: <axum::routing::future::RouterFuture<B> as core::future::future::Future>::poll::ha3aaa039e3a1cd54
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/axum-0.4.8/src/macros.rs:42
  35: <hyper::proto::h1::dispatch::Server<S,hyper::body::body::Body> as hyper::proto::h1::dispatch::Dispatch>::poll_msg::hda35a226e6f560e0
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/proto/h1/dispatch.rs:491
  36: hyper::proto::h1::dispatch::Dispatcher<D,Bs,I,T>::poll_write::hae4fc7f534b34390
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/proto/h1/dispatch.rs:297
  37: hyper::proto::h1::dispatch::Dispatcher<D,Bs,I,T>::poll_loop::h45f8006b014e2845
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/proto/h1/dispatch.rs:161
  38: hyper::proto::h1::dispatch::Dispatcher<D,Bs,I,T>::poll_inner::h7b0e9f76871f96a5
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/proto/h1/dispatch.rs:137
  39: hyper::proto::h1::dispatch::Dispatcher<D,Bs,I,T>::poll_catch::h955db4e72e7b9ab8
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/proto/h1/dispatch.rs:120
  40: <hyper::proto::h1::dispatch::Dispatcher<D,Bs,I,T> as core::future::future::Future>::poll::h126968541a4386be
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/proto/h1/dispatch.rs:424
  41: <hyper::server::conn::ProtoServer<T,B,S,E> as core::future::future::Future>::poll::h0d8b641b8484c8a6
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/server/conn.rs:1142
  42: <hyper::server::conn::upgrades::UpgradeableConnection<I,S,E> as core::future::future::Future>::poll::h2a9fb2b64056d7c4
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/server/conn.rs:1346
  43: <hyper::server::conn::spawn_all::NewSvcTask<I,N,S,E,W> as core::future::future::Future>::poll::he87cab1ebceecb94
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/hyper-0.14.17/src/server/conn.rs:1283
  44: tokio::runtime::task::core::CoreStage<T>::poll::{{closure}}::hf838d353f1f39232
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/task/core.rs:161
  45: tokio::loom::std::unsafe_cell::UnsafeCell<T>::with_mut::h5c1a5f3e29a5a536
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/loom/std/unsafe_cell.rs:14
  46: tokio::runtime::task::core::CoreStage<T>::poll::h410a4d2378fe1425
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/task/core.rs:151
  47: tokio::runtime::task::harness::poll_future::{{closure}}::h7e66f49a70a48bf4
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/task/harness.rs:467
  48: <core::panic::unwind_safe::AssertUnwindSafe<F> as core::ops::function::FnOnce<()>>::call_once::ha4ede35dc8c09d23
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/panic/unwind_safe.rs:271
  49: std::panicking::try::do_call::h9bf1526b1481658f
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/std/src/panicking.rs:406
  50: std::panicking::try::hce34bb9cb3d6f762
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/std/src/panicking.rs:370
  51: std::panic::catch_unwind::hff0de339c046ca05
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/std/src/panic.rs:133
  52: tokio::runtime::task::harness::poll_future::h22a0571f341a8fe4
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/task/harness.rs:455
  53: tokio::runtime::task::harness::Harness<T,S>::poll_inner::he829968450070f3b
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/task/harness.rs:103
  54: tokio::runtime::task::harness::Harness<T,S>::poll::hf1ae4d7dc3894514
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/task/harness.rs:57
  55: tokio::runtime::task::LocalNotified<S>::run::h23a4057f42b678c2
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/task/mod.rs:347
  56: tokio::runtime::basic_scheduler::CoreGuard::block_on::{{closure}}::{{closure}}::h6bdc27d064499238
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:532
  57: tokio::coop::with_budget::{{closure}}::he21073af0a9fe50c
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/coop.rs:102
  58: std::thread::local::LocalKey<T>::try_with::ha3868a0b480c262b
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/std/src/thread/local.rs:412
  59: std::thread::local::LocalKey<T>::with::h3b38379aec814a78
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/std/src/thread/local.rs:388
  60: tokio::coop::with_budget::he33e37f59c7ff8b0
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/coop.rs:95
  61: tokio::coop::budget::h27f9e6eaf2d6cfe1
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/coop.rs:72
  62: tokio::runtime::basic_scheduler::Context::run_task::{{closure}}::h36036a49569cf8fc
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:291
  63: tokio::runtime::basic_scheduler::Context::enter::h10fac43713f24837
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:356
  64: tokio::runtime::basic_scheduler::Context::run_task::hd09c9d487557d6ef
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:291
  65: tokio::runtime::basic_scheduler::CoreGuard::block_on::{{closure}}::he67b4b3fdfbc4ace
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:531
  66: tokio::runtime::basic_scheduler::CoreGuard::enter::{{closure}}::hde9b67ddaf06cae1
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:555
  67: tokio::macros::scoped_tls::ScopedKey<T>::set::hed655ba933b2ec0f
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/macros/scoped_tls.rs:61
  68: tokio::runtime::basic_scheduler::CoreGuard::enter::hb6b4338769eb9cba
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:555
  69: tokio::runtime::basic_scheduler::CoreGuard::block_on::h8510ffa7213dec9a
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:488
  70: tokio::runtime::basic_scheduler::BasicScheduler::block_on::hc0e1922df1329249
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/basic_scheduler.rs:168
  71: tokio::runtime::Runtime::block_on::h20934397d494fcbb
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/runtime/mod.rs:475
  72: plaque::main::h955bdc1216baefce
      at /home/amos/bearcove/plaque/src/main.rs:18
  73: core::ops::function::FnOnce::call_once::he99aaacc5fbd0766
      at /rustc/9d1b2106e23b1abd32fce1f17267604a5102f57a/library/core/src/ops/function.rs:227
                                ⋮ 15 frames hidden ⋮                              

Run with COLORBT_SHOW_HIDDEN=1 environment variable to disable frame filtering.
Run with RUST_BACKTRACE=full to include source snippets.
```

It's a pretty noisy backtrace. The async working group is [also thinking about that](https://rust-lang.github.io/wg-async/vision/roadmap/polish/stacktraces.html).

But we have _everything_ here. Well, minus the hidden frames. We got `Runtime::block_on` we used to call ourselves when we weren't using `#[tokio::main]` (proof that it's not so magic!).

We got `tokio`'s coop system that [improves tail latencies](https://tokio.rs/blog/2020-04-preemption), we got `hyper`'s http1 server, we got `axum`'s router, some more `axum` handlers, and at the very top, we have our very own `fetch_video_id`.

Okay, so now we have pretty good error reporting... but it still panics!

Well, let's do two things: one, let's make `fetch_video_id` return an error not of type `Box<dyn Error>`, but of type `color_eyre::Report`:

```
// in `src/youtube.rs`

use color_eyre::{eyre::eyre, Report};
use url::Url;

const YT_CHANNEL_ID: &str = "UCs4fQRyl1TJvoeOdekW6lYA";

#[tracing::instrument]
pub(crate) async fn fetch_video_id() -> Result<String, Report> {
    let mut api_url = Url::parse("https://www.youtube.com/feeds/videos.xml")?;
    {
        let mut q = api_url.query_pairs_mut();
        q.append_pair("channel_id", YT_CHANNEL_ID);
    }

    Err(eyre!("TODO: fetch from {api_url}"))
}
```

And two, let's... no, wait, let's not do anything and see what kind of spantrace we get now:

```
$ RUST_LOG=tower_http=debug,info cargo run --release
   Compiling plaque v0.1.0 (/home/amos/bearcove/plaque)
    Finished release [optimized + debuginfo] target(s) in 3.40s
     Running `target/release/plaque`
 INFO plaque Listening on http://0.0.0.0:3779
tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  plaque::root{}
    plaque::youtube::fetch_video_id{}
The application panicked (crashed).
Message:  called `Result::unwrap()` on an `Err` value: 
   0: TODO: fetch from https://www.youtube.com/feeds/videos.xml?channel_id=UCs4fQRyl1TJvoeOdekW6lYA

Location:
   src/youtube.rs:14

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SPANTRACE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   0: plaque::youtube::fetch_video_id
      at src/youtube.rs:6
   1: plaque::root
      at src/main.rs:35
   2: tower_http::trace::make_span::request with method=GET uri=/ version=HTTP/1.1
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/trace/make_span.rs:116

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
Location: src/main.rs:37

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SPANTRACE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   0: plaque::root
      at src/main.rs:35
   1: tower_http::trace::make_span::request with method=GET uri=/ version=HTTP/1.1
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/trace/make_span.rs:116

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
```

Okay! Nice! It shows us where the original error happened (first span trace), and then where we unwrapped it (which just happens to be the same line).

That said, we're writing a web service. We don't want to panic, we probably want to return an [HTTP 500](https://httpstatuses.com/) instead.

Is there a way to do that in axum? Yes there is! And it's actually quite interesting. Axum's `IntoReponse` trait is implemented for... `Result<T, E> where T: IntoResponse, E: IntoResponse`.

Which means we can write code like this:

```
#[tracing::instrument]
async fn root() -> Result<impl IntoResponse, (StatusCode, String)> {
    let res = youtube::fetch_video_id().await.map_err(|err| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("youtube error: {err}"),
        )
    })?;
    Ok(res)
}
```

Here, both the `Ok` and `Err` variant of `Result` contain something that can be turned into a response! The `Ok` variant is just a string (which defaults to an HTTP 200 status code), and the `Err` variant is straight up a `(StatusCode, String)`, and we're specifying HTTP 500 ourselves.

I don't love this though, I think we can improve the ergonomics a bit... because unless I specifically match on the result of some fallible function or future, I'd want it to default to HTTP 500 (Internal Server Error) - and I'd like the `?` sigil to mean that.

Luckily, `axum`'s design is flexible enough for that!

All we gotta do is make a little newtype around `eyre::Report` and then implement `IntoResponse` for it!

```
struct ReportError(Report);

impl From<Report> for ReportError {
    fn from(err: Report) -> Self {
        ReportError(err)
    }
}

impl IntoResponse for ReportError {
    fn into_response(self) -> Response {
        // {:?} shows the backtrace / spantrace, see 
        // https://docs.rs/eyre/0.6.7/eyre/struct.Report.html#display-representations
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Internal server error: {:?}", self.0),
        )
            .into_response()
    }
}
```

And now, we can change the signature of `root`, and... tada!

```
#[tracing::instrument]
async fn root() -> Result<impl IntoResponse, ReportError> {
    let res = youtube::fetch_video_id().await?;
    Ok(res)
}
```

And now, our handler doesn't panic anymore - instead, the failure is logged:

```
$ RUST_LOG=tower_http=debug,info cargo run --release
   Compiling plaque v0.1.0 (/home/amos/bearcove/plaque)
    Finished release [optimized + debuginfo] target(s) in 3.53s
     Running `target/release/plaque`
 INFO plaque Listening on http://0.0.0.0:3779
tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  plaque::root{}
    plaque::youtube::fetch_video_id{}
  
  
  0ms DEBUG tower_http::trace::on_response finished processing request, latency=0 ms, status=500
  0ms ERROR tower_http::trace::on_failure response failed, classification=Status code: 500 Internal Server Error, latency=0 ms
```

And the spantrace is sent within the HTTP response:

```
$ curl http://localhost:3779/
Internal server error: 
   0: TODO: fetch from https://www.youtube.com/feeds/videos.xml?channel_id=UCs4fQRyl1TJvoeOdekW6lYA

Location:
   src/youtube.rs:14

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SPANTRACE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   0: plaque::youtube::fetch_video_id
      at src/youtube.rs:6
   1: plaque::root
      at src/main.rs:41
   2: tower_http::trace::make_span::request with method=GET uri=/ version=HTTP/1.1
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/trace/make_span.rs:116

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
```

In a real-world application, we'd probably want to disable that for production. But that's left as an exercise to the (very patient) reader.

Okay, well. Time to hit that YouTube API.

I normally prefer to use [hyper](https://lib.rs/crates/hyper) directly instead of [reqwest](https://lib.rs/crates/reqwest), but let's use the latter to keep it short.

```
$ cargo add reqwest --no-default-features --features rustls-tls
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding reqwest v0.11.9 to dependencies with features: ["rustls-tls"]
```

The API response happens to be an Atom feed:

```
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
 <link rel="self" href="http://www.youtube.com/feeds/videos.xml?channel_id=UCs4fQRyl1TJvoeOdekW6lYA"/>
 <id>yt:channel:UCs4fQRyl1TJvoeOdekW6lYA</id>
 <yt:channelId>UCs4fQRyl1TJvoeOdekW6lYA</yt:channelId>
 <title>fasterthanlime</title>
 <link rel="alternate" href="https://www.youtube.com/channel/UCs4fQRyl1TJvoeOdekW6lYA"/>
 <author>
  <name>fasterthanlime</name>
  <uri>https://www.youtube.com/channel/UCs4fQRyl1TJvoeOdekW6lYA</uri>
 </author>
 <published>2019-10-16T09:57:58+00:00</published>
 <!-- omitted: rest of the feed -->
</feed>
```

...so let's bring in another crate to parse it:

```
$ cargo add feed-rs
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding feed-rs v1.0.0 to dependencies
```

Ooh, version 1.0.0, take a sip!

And just because I feel like being silly, let's try out [tap](https://lib.rs/crates/tap):

```
$ cargo add tap
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding tap v1.0.1 to dependencies
```

And then... weeeeeeeeeeeEEEEEEeeeee:

```
// in `src/youtube.rs`

use color_eyre::{eyre::eyre, Report};
use reqwest::Client;
use tap::Pipe;
use url::Url;

const YT_CHANNEL_ID: &str = "UCs4fQRyl1TJvoeOdekW6lYA";

#[tracing::instrument]
pub(crate) async fn fetch_video_id() -> Result<String, Report> {
    Ok(Client::new()
        .get({
            let mut url = Url::parse("https://www.youtube.com/feeds/videos.xml")?;
            url.query_pairs_mut()
                .append_pair("channel_id", YT_CHANNEL_ID);
            url
        })
        // make our mark on the world
        .header("user-agent", "cool/bear")
        .send()
        .await? // this will cover connect errors
        .error_for_status()? // this will cover HTTP errors
        .bytes()
        .await? // errors while streaming the response body?
        .pipe(|bytes| feed_rs::parser::parse(&bytes[..]))? // parse the feed
        .pipe_ref(|feed| feed.entries.get(0))
        .ok_or(eyre!("no entries in video feed"))?
        .pipe_ref(|entry| entry.id.strip_prefix("yt:video:"))
        .ok_or(eyre!("first video feed item wasn't a video"))?
        .to_string())
}
```

Whew, that's... that's a lot.

It's allllll suffix baby. Who needs statements?

Well? Let's try it out!

Oh, wait, no! Let's return it as JSON! Because we can! We'll just add the `json` feature to `axum`:

```
# in `Cargo.toml`

[dependencies]
axum = { version = "0.4.8", features = ["json"] }
```

Also add serde with its derive macros:

```
$ cargo add serde --features derive
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding serde v1.0.136 to dependencies with features: ["derive"]
```

And now our `root` handler becomes:

```
// in `src/main.rs`

// new imports:
use axum::Json;
use serde::Serialize;

#[tracing::instrument]
async fn root() -> Result<impl IntoResponse, ReportError> {
    #[derive(Serialize)]
    struct Response {
        video_id: String,
    }

    Ok(Json(Response {
        video_id: youtube::fetch_video_id().await?,
    }))
}
```

And there we go! This is what we see from `curl`:

```
$ curl -v http://localhost:3779/
*   Trying 127.0.0.1:3779...
* Connected to localhost (127.0.0.1) port 3779 (#0)
> GET / HTTP/1.1
> Host: localhost:3779
> User-Agent: curl/7.79.1
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< content-type: application/json
< content-length: 26
< date: Thu, 03 Mar 2022 23:57:30 GMT
< 
* Connection #0 to host localhost left intact
{"video_id":"nKyf4gVE5n0"}%
```

And from the server side:

```
$ RUST_LOG=tower_http=debug,info cargo run --release
    Finished release [optimized + debuginfo] target(s) in 0.05s
     Running `target/release/plaque`
 INFO plaque Listening on http://0.0.0.0:3779
tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  plaque::root{}
    plaque::youtube::fetch_video_id{}
    
  
  57ms DEBUG tower_http::trace::on_response finished processing request, latency=57 ms, status=200

tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  plaque::root{}
    plaque::youtube::fetch_video_id{}
    
  
  55ms DEBUG tower_http::trace::on_response finished processing request, latency=55 ms, status=200
```

Now we have our endpoint. How do we make it better?

Well, we're making a fresh `reqwest` `Client` for every request. That's not ideal. This is arguably _yet another_ distraction, because our plan involves caching, but if we weren't aiming for that, this might be the first thing we try: just re-use the same `Client` so we can re-use an existing connection to the YouTube server.

But first, you know what I realized? We don't really need tower's `ServiceBuilder` - I was looking at an example that had _fallible_ layers, so they needed that extra flexibility, but us? We can just turn this:

```
let app = Router::new().route("/", get(root)).layer(
        ServiceBuilder::new()
            .layer(TraceLayer::new_for_http())
            .into_inner(),
    );
```

Into this:

```
let app = Router::new()
        .route("/", get(root))
        .layer(TraceLayer::new_for_http());
```

Now: axum has a neat way to share state between handlers - and it's just another layer that adds an extension to the request! That's pretty standard hyper stuff, just wrapped nicely.

Our layer stack becomes:

```
let app = Router::new()
        .route("/", get(root))
        .layer(TraceLayer::new_for_http())
        .layer(Extension(reqwest::Client::new()));
```

A single `reqwest` Client is constructed when we build the app's layer stack, and it's accessible to any request handler that wants it, via axum extractor:

```
// in `src/main.rs`

#[tracing::instrument]
//               👇 here!
async fn root(client: Extension<reqwest::Client>) -> Result<impl IntoResponse, ReportError> {
    #[derive(Serialize)]
    struct Response {
        video_id: String,
    }

    Ok(Json(Response {
        //                      passed here 👇
        video_id: youtube::fetch_video_id(&client).await?,
    }))
}
```

And we have to change up our `fetch_video_id` function as well:

```
// in `src/youtube.rs`

#[tracing::instrument]
//                                    👇
pub(crate) async fn fetch_video_id(client: &reqwest::Client) -> Result<String, Report> {
    Ok(client
        .get({
            // (etc.)
        })
        // (etc.)
    )
}
```

Will that improve latency? Theoretically, we shouldn't have to pay the cost of a TCP handshake for subsequent requests - the connection should only be closed if it remains idle for some time.

But this is the internet. Anything can happen.

```
$ RUST_LOG=tower_http=debug cargo run --release
    Finished release [optimized + debuginfo] target(s) in 0.05s
     Running `target/release/plaque`
tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  58ms DEBUG tower_http::trace::on_response finished processing request, latency=58 ms, status=200

tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  13ms DEBUG tower_http::trace::on_response finished processing request, latency=13 ms, status=200

tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  13ms DEBUG tower_http::trace::on_response finished processing request, latency=13 ms, status=200

tower_http::trace::make_span::request{method=GET, uri=/, version=HTTP/1.1}
  0ms DEBUG tower_http::trace::on_request started processing request
  13ms DEBUG tower_http::trace::on_response finished processing request, latency=13 ms, status=200
```

Heck yeah! What do you know! Sometimes things _do_ work as expected.

But that's not what we came here for, though. It's good... but we want to be able to process a lot more traffic! The kind of traffic that will make the YouTube API servers go "please go away for a while", and then the request fails and we lose out on that sweet cross-promo. Or whatever marketing term is appropriate.

So, let's come up with schemes.

A little caching can't hurt
---------------------------

Now that we have a way to share some state across request handlers, we could put a cached version of the latest video ID in there, right?

And we'd want it to expire at some point, so maybe we store an `Instant` as well, and decide on a duration after which we consider the data stale.

Because multiple handlers can run concurrently, we want to protect that cached value with something like an `std::sync::Mutex` (we could use an `RwLock`, but let's keep it simple).

So maybe we make a new struct:

```
// in `src/main.rs`

use std::sync::{Arc, Mutex};
use std::time::Instant;

#[derive(Clone, Default)]
struct CachedLatestVideo {
    value: Arc<Mutex<Option<(Instant, String)>>>,
}
```

And then we change the `root` handler to use the cache:

```
// in `src/main.rs`

#[tracing::instrument(skip(client, cached))]
async fn root(
    client: Extension<reqwest::Client>,
    cached: Extension<CachedLatestVideo>,
) -> Result<impl IntoResponse, ReportError> {
    #[derive(Serialize)]
    struct Response {
        video_id: String,
    }

    {
        if let Some((cached_at, video_id)) = cached.value.lock().unwrap().as_ref() {
            if cached_at.elapsed() < std::time::Duration::from_secs(5) {
                return Ok(Json(Response {
                    video_id: video_id.clone(),
                }));
            } else {
                // was stale, let's refresh
                debug!("stale video, let's refresh");
            }
        } else {
            debug!("not cached, let's fetched");
        }
    }

    let video_id = youtube::fetch_video_id(&client).await?;
    cached
        .value
        .lock()
        .unwrap()
        .replace((Instant::now(), video_id.clone()));

    Ok(Json(Response { video_id }))
}
```

Because our `Mutex` is synchronous, and not asynchronous, we don't want to hold it across await points - otherwise we could deadlock: I discuss this at length in [A Rust match made in hell](https://fasterthanli.me/articles/a-rust-match-made-in-hell).

So, we lock it, check if there's a value we can use - if not, we start a fetch, and then lock it again to store it in the cache.

Is that going to make requests faster? Let's find out!

Let's run 10 requests in sequence, using `xargs` and `curl`:

```
$ xargs -I %n -P 1 /usr/bin/time --format="request %n: %e seconds (wall time)" curl -s http://localhost:3779 -o /dev/null < <(printf '%s\n' {0..9})
request 0: 0.06 seconds (wall time)
request 1: 0.00 seconds (wall time)
request 2: 0.00 seconds (wall time)
request 3: 0.00 seconds (wall time)
request 4: 0.00 seconds (wall time)
request 5: 0.00 seconds (wall time)
request 6: 0.00 seconds (wall time)
request 7: 0.00 seconds (wall time)
request 8: 0.00 seconds (wall time)
request 9: 0.00 seconds (wall time)
```

This appears to work! The first response is slow (it's a cache miss), and the others are fast (they're cache hits).

If we wait 5 seconds and repeat, we see roughly the same distribution, except the first request is faster, because it reuses the connection (0.01s instead of 0.06s).

But what happens if there's an onslaught of requests at first? Say, 5 at the same time? (Or rather, very close together?)

```
xargs -I %n -P 5 /usr/bin/time --format="request %n: %e seconds (wall time)" curl -s http://localhost:3779 -o /dev/null < <(printf '%s\n' {0..9})
request 0: 0.01 seconds (wall time)
request 1: 0.01 seconds (wall time)
request 2: 0.01 seconds (wall time)
request 7: 0.00 seconds (wall time)
request 6: 0.00 seconds (wall time)
request 5: 0.00 seconds (wall time)
rreeqquueests t8 :9 : 0.000.00  sseeccoonnddss  ((wwaallll  ttiimmee))

request 3: 0.02 seconds (wall time)
request 4: 0.03 seconds (wall time)
```

Uhhhhhhhhhhhhh...

...let's try that again:

```
$ xargs -I %n -P 5 /usr/bin/time --format="request %n: %e seconds (wall time)" curl -s http://localhost:3779 -o /dev/null < <(printf '%s\n' {0..9})
request 1: 0.01 seconds (wall time)
request 0: 0.01 seconds (wall time)
request 5: 0.00 seconds (wall time)
request 6: 0.00 seconds (wall time)
request 7: 0.00 seconds (wall time)
request 8: 0.00 seconds (wall time)
request 9: 0.00 seconds (wall time)
request 2: 0.02 seconds (wall time)
request 3: 0.02 seconds (wall time)
request 4: 0.02 seconds (wall time)
```

The requests are printed out of order, but you can see that requests 0 through 4 (inclusive) are cache misses: we did multiple concurrent fetches!

And we'd like to avoid that. They're all getting the same result anyway, so there's no point in making multiple concurrent requests to the YouTube API.

We need to do... request deduplication (or request coalescing, or single-flighting).

In our case, because we're caching the results anyway, there's really nothing preventing us from just moving to an asynchronous `Mutex`. A mutex that would let us hold guards across await points.

Since only one request can hold the lock to the cache entry, that would effectively deduplicate requests:

```
// in `src/main.rs`

// instead of std::sync::Mutex
use tokio::sync::Mutex;

#[tracing::instrument(skip(client, cached))]
async fn root(
    client: Extension<reqwest::Client>,
    cached: Extension<CachedLatestVideo>,
) -> Result<impl IntoResponse, ReportError> {
    #[derive(Serialize)]
    struct Response {
        video_id: String,
    }

    // keep that lock throughout. that's async: 👇
    let mut cached_value = cached.value.lock().await;

    {
        if let Some((cached_at, video_id)) = cached_value.as_ref() {
            if cached_at.elapsed() < std::time::Duration::from_secs(5) {
                return Ok(Json(Response {
                    video_id: video_id.clone(),
                }));
            } else {
                // was stale, let's refresh
                debug!("stale video, let's refresh");
            }
        } else {
            debug!("not cached, let's fetched");
        }
    }

    let video_id = youtube::fetch_video_id(&client).await?;
    cached_value.replace((Instant::now(), video_id.clone()));

    Ok(Json(Response { video_id }))
}
```

Let's try this again:

```
$ xargs -I %n -P 5 /usr/bin/time --format="request %n: %e seconds (wall time)" curl -s http://localhost:3779 -o /dev/null < <(printf '%s\n' {0..9})
request 2: request 0: 0.01 seconds (warll etqiumees)t
 4: 0.01 seconds (wall time)
0.01 seconds (wall time)
request 1: 0.01 seconds (wall time)
request 3: 0.01 seconds (wall time)
request 5: 0.00 seconds (wall time)
request 8: 0.00 seconds (wall time)
rreeqquueesstt  67::  0.00 seconds (0.00w aslelc otnidmse )(
wall time)
request 9: 0.00 seconds (wall time)
```

Oh boy. Maybe using `xargs` for this was a mistake. We could probably just use `oha` right? Make it do 10 requests with 5 clients, the latency distributions should show us cached / uncached requests:

```
$ oha -n 10 -c 5 http://localhost:3779
(cut)
Response time histogram:
  0.007 [5] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.015 [0] |
  0.022 [0] |
  0.029 [0] |
  0.037 [0] |
  0.044 [0] |
  0.051 [0] |
  0.059 [0] |
  0.066 [0] |
  0.073 [0] |
  0.081 [5] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
```

There, beautiful! 5 cache misses, 5 cache hits.

But I don't like this method: it only really works if you have one cache key.

Otherwise, if you have something like that:

```
#[derive(Clone, Default)]
struct CachedLatestVideos {
    value: Arc<Mutex<HashMap<ChannelId, (Instant, LatestVideoId)>>>,
}
```

(Where `ChannelId` and `LatestVideoId` are just newtypes for `String` to make our type signature readable)

...then requests for the latest video of channel A would block requests for the latest video of channel B, even if those were fresh and in cache.

A problem we can solve with ~even more violence~ even more mutexes, something like that:

```
#[derive(Clone, Default)]
struct CachedLatestVideos {
    value: Arc<Mutex<HashMap<ChannelId, CachedVideoSlot>>>
}

#[derive(Clone, Default)]
struct CachedVideoSlot {
    value: Arc<Mutex<Option<(Instant, LatestVideoId)>>>,
}
```

That might work, I just... I just find myself yearning for something a little more elegant. I need a little more grace in my life, not more locks.

And I'd also like to stick with synchronous locks: the shorter we hold them, the better.

We should be able to:

*   Acquire the lock
*   If there's a fresh value in cache, get it and release the lock
*   Otherwise, if there's an in-flight request, subscribe to it and release the lock
*   Otherwise, start our own request (and let other requests subscribe to it) and release the lock while it's in-flight

And there's a surprising amount of subtlety around doing just that!

My instinct tells me "we're gonna need channels": we essentially need a channel from the "task", the "in-flight request" that we can receive a value from.

But there could be multiple subscribers for the same in-flight request, so we can't use an [mpsc channel](https://docs.rs/tokio/latest/tokio/sync/mpsc/fn.channel.html), the most common kind of channel: it's multi-producer (`Sender` is `Clone`), but single-consumer.

Instead, we want a [broadcast channel](https://docs.rs/tokio/latest/tokio/sync/broadcast/index.html), which is multi-producer, multi-consumer.

What's interesting here is that `Receiver` is not `Clone` - so we can't store a `Receiver` in our state, we have to store a `Sender`, and subscribe to it.

Let's see what a naive version would look like:

```
// in `src/main.rs`

// back to sync mutexes (instead of `tokio::sync::Mutex`)
use std::sync::Mutex;
use tokio::sync::broadcast;

#[derive(Clone, Default)]
struct CachedLatestVideo {
    inner: Arc<Mutex<CachedLastVideoInner>>,
}

#[derive(Default)]
struct CachedLastVideoInner {
    last_fetched: Option<(Instant, String)>,
    inflight: Option<broadcast::Sender<Result<String, Box<dyn Error>>>>,
}
```

Immediately, we run into issues: we can't send `Box<dyn Error>` between threads: and we definitely will, because various request handlers all run in different tasks, which might be scheduled on different OS threads.

So, let's ask for the `Send` and `Sync` bounds as well:

```
#[derive(Default)]
struct CachedLastVideoInner {
    last_fetched: Option<(Instant, String)>,
    // here
    inflight: Option<broadcast::Sender<Result<String, Box<dyn Error + Sync + Send>>>>,
}
```

Then, we run into some _more_ problems because... whatever values are sent to a broadcast channel need to be `Clone`. Which make sense: each consumer will get its own copy (its own clone, I guess) of the value. And we didn't ask for the Error type to be `Clone`, so let's add one more bound...

```
inflight: Option<broadcast::Sender<Result<String, Box<dyn Error + Sync + Send + Clone>>>>,
```

But then...

```
error[E0225]: only auto traits can be used as additional traits in a trait object
  --> src/main.rs:42:85
   |
42 |     inflight: Option<broadcast::Sender<Result<String, Box<dyn Error + Sync + Send + Clone>>>>,
   |                                                               -----                 ^^^^^ additional non-auto trait
   |                                                               |
   |                                                               first non-auto trait
   |
   = help: consider creating a new trait with all of these as supertraits and using that trait here instead: `trait NewTrait: StdError + Clone {}`
   = note: auto-traits like `Send` and `Sync` are traits that have special properties; for more information on them, visit <https://doc.rust-lang.org/reference/special-types-and-traits.html#auto-traits>
```

Mhhh we might be on the wrong road here. I'm not even sure all the errors we could possibly get are `Clone` anyway (or `Send`, or `Sync`). Instead, let's just make an error type that carries the human-readable string representation of the error.

```
$ cargo add thiserror
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding thiserror v1.0.30 to dependencies
```

```
// in `src/main.rs`

#[derive(Debug, Clone, thiserror::Error)]
#[error("stringified error: {inner}")]
pub struct CachedError {
    inner: String,
}

impl CachedError {
    pub fn new<E: std::fmt::Display>(e: E) -> Self {
        Self {
            inner: e.to_string(),
        }
    }
}

impl From<Report> for CachedError {
    fn from(e: Report) -> Self {
        CachedError::new(e)
    }
}

impl From<broadcast::error::RecvError> for CachedError {
    fn from(e: broadcast::error::RecvError) -> Self {
        CachedError::new(e)
    }
}

// and for completeness

impl From<CachedError> for ReportError {
    fn from(err: CachedError) -> Self {
        ReportError(err.into())
    }
}
```

Now we can have this be our error type, which is automatically `Send` and `Sync`, also `Clone` because we derived it, and implements `std::error::Error` thanks to [thiserror](https://lib.rs/crates/thiserror).

```
#[derive(Default)]
struct CachedLastVideoInner {
    last_fetched: Option<(Instant, String)>,
    inflight: Option<broadcast::Sender<Result<String, CachedError>>>,
}
```

And now we "just" have to implement our deduplicating handler:

```
#[tracing::instrument(skip(client, cached))]
async fn root(
    client: Extension<reqwest::Client>,
    cached: Extension<CachedLatestVideo>,
) -> Result<impl IntoResponse, ReportError> {
    #[derive(Serialize)]
    struct Response {
        video_id: String,
    }

    // keep that lock throughout
    let mut inner = cached.inner.lock().unwrap();

    if let Some((fetched_at, video_id)) = inner.last_fetched.as_ref() {
        // is it fresh?
        if fetched_at.elapsed() < std::time::Duration::from_secs(5) {
            return Ok(Json(Response {
                video_id: video_id.clone(),
            }));
        } else {
            // was stale, let's refresh
            debug!("stale video, let's refresh");
        }
    }

    // is there an in-flight request?
    if let Some(inflight) = inner.inflight.as_ref() {
        // yes, subscribe to it!
        let mut rx = inflight.subscribe();
        let video_id = rx
            .recv()
            .await
            .map_err(|_| eyre!("in-flight request died"))??;
        debug!("received deduplicated fetch");
        return Ok(Json(Response { video_id }));
    }

    // there isn't, let's fetch
    let (tx, mut rx) = broadcast::channel::<Result<String, CachedError>>(1);
    tokio::spawn(async move {
        let video_id = youtube::fetch_video_id(&client).await;
        match video_id {
            Ok(video_id) => {
                inner
                    .last_fetched
                    .replace((Instant::now(), video_id.clone()));
                tx.send(Ok(video_id))
            }
            Err(e) => tx.send(Err(e.into())),
        };
    });
    let video_id = rx
        .recv()
        .await
        .map_err(|_| eyre!("in-flight request died"))??;
    debug!("received deduplicated fetch");
    Ok(Json(Response { video_id }))
}
```

This code is wrong, and thankfully, the Rust compiler catches it:

```
$ cargo check
    Checking plaque v0.1.0 (/home/amos/bearcove/plaque)
error: future cannot be sent between threads safely
   --> src/main.rs:124:5
    |
124 |     tokio::spawn(async move {
    |     ^^^^^^^^^^^^ future created by async block is not `Send`
    |
    = help: within `impl Future<Output = [async output]>`, the trait `Send` is not implemented for `std::sync::MutexGuard<'_, CachedLastVideoInner>`
note: captured value is not `Send`
   --> src/main.rs:128:17
    |
128 |                 inner
    |                 ^^^^^ has type `std::sync::MutexGuard<'_, CachedLastVideoInner>` which is not `Send`
note: required by a bound in `tokio::spawn`
   --> /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tokio-1.17.0/src/task/spawn.rs:127:21
    |
127 |         T: Future + Send + 'static,
    |                     ^^^^ required by this bound in `tokio::spawn`

error: could not compile `plaque` due to previous error
```

Woops! We actually sent a `MutexGuard` across threads (by spawning a task, which may be scheduled on any thread).

It's a good thing the compiler caught it, because that's not what we meant to do: we didn't want to hang onto that lock, we wanted to release it and re-acquire it when we fill in the result.

Also, we forgot to store the sender in `inner.inflight` and clear it when it's done. But even more importantly: when we subscribe to an in-flight task, we keep holding onto the `inner` lock! That would've been a deadlock.

The compiler catches this, too, but the message isn't great this time:

```
$ cargo check
    Checking plaque v0.1.0 (/home/amos/bearcove/plaque)
error[E0277]: the trait bound `fn(Extension<reqwest::Client>, Extension<CachedLatestVideo>) -> impl Future<Output = Result<Opaque(DefId(0:229 ~ plaque[f569]::root::{opaque#0}::{opaque#0}), []), ReportError>> {root}: axum::handler::Handler<_, _>` is not satisfied
   --> src/main.rs:76:25
    |
76  |         .route("/", get(root))
    |                     --- ^^^^ the trait `axum::handler::Handler<_, _>` is not implemented for `fn(Extension<reqwest::Client>, Extension<CachedLatestVideo>) -> impl Future<Output = Result<Opaque(DefId(0:229 ~ plaque[f569]::root::{opaque#0}::{opaque#0}), []), ReportError>> {root}`
    |                     |
    |                     required by a bound introduced by this call
    |
note: required by a bound in `axum::routing::get`
   --> /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/axum-0.4.8/src/routing/method_routing.rs:394:1
    |
394 | top_level_handler_fn!(get, GET);
    | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `axum::routing::get`
    = note: this error originates in the macro `top_level_handler_fn` (in Nightly builds, run with -Z macro-backtrace for more info)

For more information about this error, try `rustc --explain E0277`.
error: could not compile `plaque` due to previous error
```

So this time, we'll have to think a little: we _only_ want to do synchronous things while holding onto that lock guard: we _cannot_ `.await` anything.

So, we'll have to get a little creative. To be entirely safe, we'll use a scope to limit how long we hold the lock - to make sure that when we're out of this scope, the lock is released.

Something like this:

```
fn() {
    let whatever = {
        let inner = cached.inner.lock().unwrap();

        // do sync stuff with `inner`
    };

    // do async stuff with `whatever`
}
```

Giving, with real code, this:

```
#[tracing::instrument(skip(client, cached))]
async fn root(
    client: Extension<reqwest::Client>,
    cached: Extension<CachedLatestVideo>,
) -> Result<impl IntoResponse, ReportError> {
    #[derive(Serialize)]
    struct Response {
        video_id: String,
    }

    let mut rx = {
        // only sync code in this block
        let mut inner = cached.inner.lock().unwrap();

        if let Some((fetched_at, video_id)) = inner.last_fetched.as_ref() {
            // is it fresh?
            if fetched_at.elapsed() < std::time::Duration::from_secs(5) {
                return Ok(Json(Response {
                    video_id: video_id.clone(),
                }));
            } else {
                // was stale, let's refresh
                debug!("stale video, let's refresh");
            }
        }

        // is there an in-flight request?
        if let Some(inflight) = inner.inflight.as_ref() {
            inflight.subscribe()
        } else {
            // there isn't, let's fetch
            let (tx, rx) = broadcast::channel::<Result<String, CachedError>>(1);
            inner.inflight = Some(tx.clone());
            let cached = cached.clone();
            tokio::spawn(async move {
                let video_id = youtube::fetch_video_id(&client).await;

                {
                    // only sync code in this block
                    let mut inner = cached.inner.lock().unwrap();
                    inner.inflight = None;

                    match video_id {
                        Ok(video_id) => {
                            inner
                                .last_fetched
                                .replace((Instant::now(), video_id.clone()));
                            let _ = tx.send(Ok(video_id));
                        }
                        Err(e) => {
                            let _ = tx.send(Err(e.into()));
                        }
                    };
                }
            });
            rx
        }
    };

    // if we reached here, we're waiting for an in-flight request (we weren't
    // able to serve from cache)
    Ok(Json(Response {
        video_id: rx
            .recv()
            .await
            .map_err(|_| eyre!("in-flight request died"))??,
    }))
}
```

And that appears to work:

```
$ oha -n 10 -c 5 http://localhost:3779
(cut)
Response time histogram:
  0.005 [5] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.011 [0] |
  0.016 [0] |
  0.022 [0] |
  0.027 [0] |
  0.033 [0] |
  0.038 [0] |
  0.044 [0] |
  0.049 [0] |
  0.055 [0] |
  0.060 [5] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
```

Making it generic
-----------------

Chances are, that's not the only thing we want to cache! And if we have [three or more](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)), we won't want to copy-paste that code everywhere.

Well, no big deal, we'll just make it generic!

In fact, let's move all caching/deduplication-related code to its own module:

```
// in `src/main.rs`

mod cached;
use cached::{CachedError, Cached};
```

```
// in `src/cached.rs`

use std::{
    sync::{Arc, Mutex},
    time::{Duration, Instant},
};

use color_eyre::{eyre::eyre, Report};
use tokio::sync::broadcast;
use tracing::debug;

#[derive(Debug, Clone, thiserror::Error)]
#[error("stringified error: {inner}")]
pub struct CachedError {
    inner: String,
}

impl CachedError {
    pub fn new<E: std::fmt::Display>(e: E) -> Self {
        Self {
            inner: e.to_string(),
        }
    }
}

impl From<Report> for CachedError {
    fn from(e: Report) -> Self {
        CachedError::new(e)
    }
}

impl From<broadcast::error::RecvError> for CachedError {
    fn from(e: broadcast::error::RecvError) -> Self {
        CachedError::new(e)
    }
}

#[derive(Clone)]
pub struct Cached<T>
where
    T: Clone + Send + Sync + 'static,
{
    inner: Arc<Mutex<CachedLastVideoInner<T>>>,
    refresh_interval: Duration,
}

struct CachedLastVideoInner<T>
where
    T: Clone + Send + Sync + 'static,
{
    last_fetched: Option<(Instant, T)>,
    inflight: Option<broadcast::Sender<Result<T, CachedError>>>,
}

impl<T> Default for CachedLastVideoInner<T>
where
    T: Clone + Send + Sync + 'static,
{
    fn default() -> Self {
        Self {
            last_fetched: None,
            inflight: None,
        }
    }
}

impl<T> Cached<T>
where
    T: Clone + Send + Sync + 'static,
{
    pub fn new(refresh_interval: Duration) -> Self {
        Self {
            inner: Default::default(),
            refresh_interval,
        }
    }

    pub async fn get_cached(&self) -> Result<T, CachedError> {
        let mut rx = {
            // only sync code in this block
            let mut inner = self.inner.lock().unwrap();

            if let Some((fetched_at, value)) = inner.last_fetched.as_ref() {
                if fetched_at.elapsed() < self.refresh_interval {
                    return Ok(value.clone());
                } else {
                    debug!("stale, let's refresh");
                }
            }

            if let Some(inflight) = inner.inflight.as_ref() {
                inflight.subscribe()
            } else {
                // there isn't, let's fetch
                let (tx, rx) = broadcast::channel::<Result<T, CachedError>>(1);
                inner.inflight = Some(tx.clone());
                let inner = self.inner.clone();
                tokio::spawn(async move {
                    let res = todo!("how do we actually perform a request?");

                    {
                        // only sync code in this block
                        let mut inner = inner.lock().unwrap();
                        inner.inflight = None;

                        match res {
                            Ok(value) => {
                                inner.last_fetched.replace((Instant::now(), value.clone()));
                                let _ = tx.send(Ok(value));
                            }
                            Err(e) => {
                                let _ = tx.send(Err(e.into()));
                            }
                        };
                    }
                });
                rx
            }
        };

        // if we reached here, we're waiting for an in-flight request (we weren't
        // able to serve from cache)
        Ok(rx
            .recv()
            .await
            .map_err(|_| eyre!("in-flight request died"))??)
    }
}
```

There's just one little wrinkle... as the `todo!` mentions: how do we actually perform a request? Where do we get our values from? That too, needs to be generic.

We could take a future directly, but that means we'd need to build a future (e.g. call `youtube::fetch_video_id` without awaiting it) every time we want to call `get_cached` - and that's unnecessary work.

Here's my take: instead, let's accept a closure that can build a future. Here I'll assume that it's okay to heap-allocate in that code path, so we'll have it return a boxed future for simplicity. Our implementation of `youtube::fetch_video_id` is an async fn anyway, so its future type cannot be named, as of Rust 1.59.0 stable, unless I'm missing something.

So, quick type alias:

```
// in `src/cached.rs`

use std::future::Future;

pub type BoxFut<'a, O> = Pin<Box<dyn Future<Output = O> + Send + 'a>>;
```

And let's accept a function returning a boxed future that returns a `T` (and can fail! with any error type that we know how to display!)

```
// in `src/cached.rs`

    pub async fn get_cached<F, E>(&self, f: F) -> Result<T, CachedError>
    where
        F: FnOnce() -> BoxFut<'static, Result<T, E>> + Send + 'static,
        E: std::fmt::Display + 'static,
    {
        // (cut)
    }
```

And our code becomes:

```
// in `src/cached.rs`

            if let Some(inflight) = inner.inflight.as_ref() {
                inflight.subscribe()
            } else {
                // there isn't, let's fetch
                let (tx, rx) = broadcast::channel::<Result<T, CachedError>>(1);
                inner.inflight = Some(tx.clone());
                let inner = self.inner.clone();

                // call the closure first, so we don't send _it_ across threads,
                // just the Future it returns
                let fut = f();

                tokio::spawn(async move {
                    let res = fut.await;

                    {
                        // only sync code in this block
                        let mut inner = inner.lock().unwrap();
                        inner.inflight = None;

                        match res {
                            Ok(value) => {
                                inner.last_fetched.replace((Instant::now(), value.clone()));
                                let _ = tx.send(Ok(value));
                            }
                            Err(e) => {
                                let _ = tx.send(Err(CachedError {
                                    inner: e.to_string(),
                                }));
                            }
                        };
                    }
                });
                rx
            }
```

Now to use our beautifully generic code for real:

```
// in `src/main.rs`

#[derive(Clone)]
struct LatestVideo(String);
```

Our layer stack becomes this:

```
let app = Router::new()
        .route("/", get(root))
        .layer(TraceLayer::new_for_http())
        .layer(Extension(reqwest::Client::new()))
        .layer(Extension(Cached::<LatestVideo>::new(Duration::from_secs(
            5,
        ))));
```

And `root`, just this:

```
#[tracing::instrument(skip(client, cached))]
async fn root(
    client: Extension<reqwest::Client>,
    cached: Extension<Cached<LatestVideo>>,
) -> Result<impl IntoResponse, ReportError> {
    #[derive(Serialize)]
    struct Response {
        video_id: String,
    }

    let LatestVideo(video_id) = cached
        .get_cached(|| {
            Box::pin(async move {
                let video_id = youtube::fetch_video_id(&client).await?;
                Ok::<_, Report>(LatestVideo(video_id))
            })
        })
        .await?;

    Ok(Json(Response { video_id }))
}
```

That's.. nice! Well, there's a box-pinned async-move block in a closure, and we have to use a lil' [turbofish](https://turbo.fish/) to let the compiler know the error type, but we've separated concerns, so as far as I'm concerned: mission accomplished.

If the cached items were keyed, we could easily imagine that the outer `Cached` structure had a `HashMap` of `CachedInner` instead: we'd still have a single lock, which would only ever be held for very short periods of time.

In a production app, we might actually want to have a _negative_ cache as well: if we can't fetch the video for some reason, and it fails _almost immedialy_, we wouldn't want to hammer YouTube's API servers with requests. We'd want to sleep between retries, and have our handler either wait for some retries, or immediately return an error.

We also might want to set a timeout on that HTTP request: I don't think there's any timeouts (connection timeout, idle read/write timeout) on that default reqwest client, and that usually makes me nervous. Timeout all the things, always!

But that's not what I'm concerned with - y'all can solve all of these on your own.

What I'm concerned with is we left a terrific, horrific bug in there. One that, in a past ~life~ day job, led to a pretty bad incident that was really hard to investigate.

Panic! at the in-flight request
-------------------------------

What happens if any part of our code panics? That's something we need to think about, and that Rust protects us _less than usual_ from. They're not safety concerns, "just" logic errors.

Let's make... the 3rd request panic.

```
// in `src/cached.rs`

use std::sync::atomic::{AtomicU64, Ordering};

static DOOM_COUNTER: AtomicU64 = AtomicU64::new(0);

impl<T> Cached<T>
where
    T: Clone + Send + Sync + 'static,
{
    pub async fn get_cached<F, E>(&self, f: F) -> Result<T, CachedError>
    where
        F: FnOnce() -> BoxFut<'static, Result<T, E>>,
        E: std::fmt::Display + 'static,
    {
        if DOOM_COUNTER.fetch_add(1, Ordering::SeqCst) == 2 {
            panic!("doom!");
        }

        // etc.
    }
}
```

```
$ oha -n 10 -c 5 http://localhost:3779

Status code distribution:
  [200] 9 responses

Error distribution:
  [1] connection closed before message completed
```

Okay, that's fine - only the third request was impacted. Because our handler panicked, axum/hyper just closed the connection. Seems like a reasonable response, even though if we wanted, we could probably catch the panic and turn it into a 500 instead.

Now let's panic someplace else! Say, after we've acquired the lock:

```
pub async fn get_cached<F, E>(&self, f: F) -> Result<T, CachedError>
    where
        F: FnOnce() -> BoxFut<'static, Result<T, E>>,
        E: std::fmt::Display + 'static,
    {
        let mut rx = {
            // only sync code in this block
            let mut inner = self.inner.lock().unwrap();

            if DOOM_COUNTER.fetch_add(1, Ordering::SeqCst) == 2 {
                panic!("doom!");
            }

            // etc.
        };

        // if we reached here, we're waiting for an in-flight request (we weren't
        // able to serve from cache)
        Ok(rx
            .recv()
            .await
            .map_err(|_| eyre!("in-flight request died"))??)
    }
```

Now, oha never completes: it's stuck in the TUI with 8"connection closed before the message completed", and 2 requests that just... never complete.

Our server logs tell the story:

```
The application panicked (crashed).
Message:  called `Result::unwrap()` on an `Err` value: PoisonError { .. }
Location: src/cached.rs:91

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SPANTRACE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   0: plaque::root
      at src/main.rs:49
   1: tower_http::trace::make_span::request with method=GET uri=/ version=HTTP/1.1
      at /home/amos/.cargo/registry/src/github.com-1ecc6299db9ec823/tower-http-0.2.3/src/trace/make_span.rs:116

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
```

Because we panicked while holding a `MutexGuard`, the mutex is now poisoned, and nobody can ever acquire it again.

So what happens is:

*   The first request finds nothing in cache, starts a task
*   The second task finds an in-flight request, subscribes to it
*   The third task acquires the lock, panics holding it
*   Tasks 4 through 10 panic as they try to acquire the poisoned lock

The first and second requests are waiting for a task that will never complete, because it too, panicked while trying to acquire the poisoned lock. So we get eight connection resets, and two requests stuck forever.

I guess that's where tower's [timeout facilities](https://docs.rs/tower/latest/tower/builder/struct.ServiceBuilder.html#method.timeout) would come in handy, to have those requests eventually fail.

Yes! Timeout _all the things_.

Told you there was subtlety!

But that's not even the bug I'm getting at. And that one's pretty easy to solve: we can just switch to a non-poisoning `Mutex`, like [parking_lot](https://lib.rs/crates/parking_lot)'s.

```
$ cargo add parking_lot
    Updating 'https://github.com/rust-lang/crates.io-index' index
      Adding parking_lot v0.12.0 to dependencies
```

We just need to swap `std::sync::Mutex` with `parking_lot::Mutex`, and remove a couple `.unwrap()` calls, since `parking_lot::Mutex::unlock()` is infallible.

And now, still with the third request panicking while holding the lock, we have:

```
$ oha -n 10 -c 5 http://localhost:3779
(cut)
Status code distribution:
  [200] 9 responses

Error distribution:
  [1] connection closed before message completed
```

...just the third request failing, exactly what we wanted.

But now... what if we panic _in the task itself_? In the "in-flight request"?

Let's panic only the first time, this time:

```
tokio::spawn(async move {
                    let res = fut.await;

                    if DOOM_COUNTER.fetch_add(1, Ordering::SeqCst) == 0 {
                        panic!("doom!");
                    }

                    {
                        // only sync code in this block
                        let mut inner = inner.lock();
                        inner.inflight = None;

                        // etc.
                    }
                });
```

In _that_ case, we do see the panic in the server logs:

```
The application panicked (crashed).
Message:  doom!
Location: src/cached.rs:118

Backtrace omitted. Run with RUST_BACKTRACE=1 environment variable to display it.
Run with RUST_BACKTRACE=full to include source snippets.
```

But from the outside, all we see is that all requests are stuck.

_All_ requests.

Not just the first one, not just for the first five seconds, all requests, forever.

And that's what my big bad dayjob incident was about: a bunch of in-flight requests got in a bad state, and so we'd be forever stuck waiting for them, long past any chance they'd ever complete, and never starting new requests.

To make matters worse, it wasn't even a panic! That's just the example I've chosen to show you the bug. A panic would've been caught by the [Sentry](https://sentry.io/welcome/) reporter, and we'd have received an alert about it.

No, it was a timeout. The task was simply taking longer than a few seconds, and it was timed out - which in Rust, amounts to just dropping the future.

And with an [MPSC channel](https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html), you can detect that condition: if you hold a `Receiver` and all `Sender`s are dropped, the future returned by `recv` just yields `None` - that would be our cue that something went wrong with the in-flight request, and we're at liberty to try again.

But here... there's no such thing! Because the only way to be able to subscribe to the result of the in-flight request is to hold a `Sender`. So there's two places holding a `Sender` for the same channel: the in-flight request _and_ our mutex-protected state.

If the in-flight request doesn't run to completion, it never replaces `inner.inflight` with `None`, and the channel is never closed. A bug reminiscent of the Go channel spaghetti I find everywhere I look.

So..... how do we solve this?

Well!

We'd like the channel to close whether the task completes successfully or panics. Which is to say, we'd like the `Sender` to drop either way. _All_ senders for that channel.

We can't _not_ hold a `Sender` in our internal state, because that's how we subscribe to in-flight tasks (unless we want to go back to the two-level mutex solution I hinted at above).

But maybe we can hold a reference to `Sender` that... doesn't prevent it from dropping.

A reference that would let us access the `Sender` _if it still exists_, if it hasn't been dropped by the in-flight request yet.

And that's exactly what [Weak](https://doc.rust-lang.org/stable/std/sync/struct.Weak.html) lets us do: it's a version of [Arc](https://doc.rust-lang.org/stable/std/sync/struct.Arc.html) that holds a _non-owning reference_ to a `T`.

That way:

*   The task will hold an `Arc<Sender>`, and it _will_ drop it whether it panics or completes successfully
*   The internal state will hold a `Weak<Sender>`, which won't prevent the `Sender` from being dropped

And to access the `Sender` from the state (when we want to subscribe to its result), we simply use [Weak::upgrade](https://doc.rust-lang.org/stable/std/sync/struct.Weak.html#method.upgrade), which returns an `Option<Arc<T>>`. If we get a `Some`, we know the task is still alive. If we get a `None`, we know it's not.

But isn't that a race condition? Couldn't we get an `Arc<Sender>` _right before the task finishes_, and then we'd never receive anything?

No, because we're only ever manipulating `inner.inflight` while holding a lock.

So, without further ado, here's my idea of a fix:

```
// in `src/cached.rs`

use std::sync::Weak;

struct CachedLastVideoInner<T>
where
    T: Clone + Send + Sync + 'static,
{
    last_fetched: Option<(Instant, T)>,
    // now weak!      👇
    inflight: Option<Weak<broadcast::Sender<Result<T, CachedError>>>>,
}

impl<T> Cached<T>
where
    T: Clone + Send + Sync + 'static,
{
    pub async fn get_cached<F, E>(&self, f: F) -> Result<T, CachedError>
    where
        F: FnOnce() -> BoxFut<'static, Result<T, E>>,
        E: std::fmt::Display + 'static,
    {
        let mut rx = {
            let mut inner = self.inner.lock();

            if let Some((fetched_at, value)) = inner.last_fetched.as_ref() {
                // etc.
            }

            // it's only in-flight if we can upgrade it to an `Arc`:  👇👇👇
            if let Some(inflight) = inner.inflight.as_ref().and_then(Weak::upgrade) {
                inflight.subscribe()
            } else {
                let (tx, rx) = broadcast::channel::<Result<T, CachedError>>(1);
                // let's reference-count a single `Sender`:
                let tx = Arc::new(tx);
                // and only store a weak reference in our state:
                //                            👇
                inner.inflight = Some(Arc::downgrade(&tx));
                let inner = self.inner.clone();

                let fut = f();

                tokio::spawn(async move {
                    let res = fut.await;

                    // still testing that panic...
                    if DOOM_COUNTER.fetch_add(1, Ordering::SeqCst) == 0 {
                        panic!("doom!");
                    }

                    {
                        // etc.
                    }
                });
                rx
            }
        };

        // etc.
    }
}
```

And let me tell you, I was pretty pleased with myself when I found this pattern.

(That's _not_ the fix we used at that dayjob: I went with something a lot more complicated with a `Drop` impl and everything. This solution is pretty elegant in comparison).

Let's take it for a test-drive.

Here's our first batch of requests:

```
$ oha etc.
Status code distribution:
  [200] 5 responses
  [500] 5 responses
```

And the second:

```
$ oha etc.
Status code distribution:
  [200] 10 responses
```

Now, a task dying simply makes room for another one. And we get nice 500 errors that look like this:

```
$ curl http://localhost:3779          
Internal server error: 
   0: stringified error: in-flight request died
```

...because it's the `rx.recv()` call that fails, and that doesn't panic, it just propagates the error all the way up, which gets turned into a 500 by our `impl IntoResponse for ReportError`.

And that's all I wanted to show y'all today!

Until next time, take excellent care of yourselves.

This article was made possible thanks to my patrons: tonygo_, queenfartbutt, asaaki, Jonathan Knapp, Julien Roncaglia, Jonathan Strickland, Ted Mielczarek, Michael Watzko, MW, Chad Birch, Justin Ossevoort, Maximilian, Olivia Crain, Ives van Hoorne, Matt Jadczak, Prince Wilson, Thomas Corbin, Rasmus Larsen, Jane Lusby, Benjamin Röjder Delnavaz, Vladyslav Batyrenko, koivunej, Pete Bevin, Andronik, Douglas Creager and 119 more

参考：

* [Request coalescing in async Rust](https://fasterthanli.me/articles/request-coalescing-in-async-rust)
