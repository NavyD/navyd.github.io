---
title: "Rust Unsafe Pointer Types Need an Overhaul"
date: 2022-03-28T20:56:16+08:00
draft: true
tags: [rust, unsafe]
---

> 原文地址 [gankra.github.io](https://gankra.github.io/blah/fix-rust-pointers/)

I think about unsafe pointers in Rust a lot.

I literally wrote the book on unsafe Rust. And the book on pointers in Rust. And redesigned the Rust’s pointer APIs. And designed the standard library’s abstraction for unsafe heap-allocated buffers. And maintain the alternative Vec layout.

I think about unsafe pointers in Rust a lot, and I absolutely hate them.

Don’t get me wrong, I think all of the above work has made them better but they are still deeply flawed. Actually they’ve gotten a lot worse. Not because the APIs have changed, but because when I was working on this stuff we had too naive of an understanding of how pointers should work. Others have done a lot of great work to expand this understanding, and now the flaws are all the more glaring.

This article is broken up into 3 parts: conceptual background, problems with the current design, and proposed solutions.

1 Background
This section can be skipped entirely if you know everything about computers.

1.1 Aliasing
Aliasing is a very important concept in compilers and language semantics. At a high-level, it’s the study of the observability of modifications to memory. We call it aliasing because the problem is very easy until you can refer to a piece of memory in more than one way. Pointers are just nicknames for memory.

The primary function of aliasing is as a model for when the compiler can semantically cache memory accesses. This can either mean assuming a value in memory hasn’t been modified or assuming a write to memory isn’t necessary. This is exceptionally important because essentially all program state is semantically in memory. It’s impossible for a general purpose programming language that does anything on the behalf of the programmer to allow arbitrary reads and writes to memory.

As a hopefully extremely obvious example that we can all agree on, a compiler should be able to assume that the following program will pass 1 to `println!`:

```rust
let mut x = 0;
let mut y = 1; // Wouldn't it be fucked up if this could modify y?
x = 2;

println!("{}", y);
```

When we talk about aliasing we usually jump immediately to pointers because that’s the hard part but like, the fact that this has deterministic behaviour is part of your aliasing model! Variables are semantically unaliased until you actually take a reference to them!

This is actually a foundational assumption for putting things in registers, because putting something in a register is caching it. If a compiler can’t decide it’s ok to put values in general purpose registers or spill them to the stack, it’s an assembler _at best_. We would like to build languages that are higher-level than an assembler!

With the “no really you need this no matter what” part out of the way, let’s talk about how pointers make this hard. In the following function, can we assume that `input` and `output` refer to different regions of memory?

```
fn compute(input: &u32, output: &mut u32) {
    if *input > 10 {
        *output = 1;
    }
    if *input > 5 {
        *output *= 2;
    }
}
```

If we can, then the compiler is free to rewrite it as follows:

```
fn compute(input: &u32, output: &mut u32) {
    // keep `*input` in a register
    let cached_input = *input; 
    if cached_input > 10 {
        // If the original, > 10 would imply:
        //
        // *output = 1
        // *output *= 2
        //
        // which we can just simplify into:
        *output = 2;
    } else if cached_input > 5 {
        *output *= 2;
    }
}
```

If they _do_ point to overlapping memory, then the write `*output = 1` would affect the result of the read `*input > 5`, and we say those accesses _alias_. When we perform (potentially) aliasing accesses, the compiler has to conservatively load and store from memory as much as the source code implies.

Now it’s often clumsy to talk about _accesses_ aliasing, so we usually talk about _pointers_ aliasing as a shorthand. So one would reasonably say that `input` and `output` alias each other. The reason that the _actual_ model is in terms of _accesses_ and not _pointers_ is because that’s the thing that we care about.

We don’t _actually_ care if you pass in two pointers that “alias” but:

*   Only one of them is ever used (no second observer)
*   Both only read (a read can’t observably affect another read) (this assumption is why memory mapped hardware has to use `volatile`)

This is also why Rust has such a distinct schism between “unique mutable” references (`&mut`) and “shared immutable” references (`&`). It’s fine to make as many copies as you want of readonly pointers, but if you want to actually write to memory it’s really important to know how it’s aliased!

(You may notice that this is a simplified model full of lies, if you would like less lies, read my extremely detailed [discussion of Stacked Borrows](https://rust-unofficial.github.io/too-many-lists/fifth-stacked-borrows.html).)

Here are some other useful shorthands:

*   memory is **anonymous** if the programmer cannot refer to it by name or pointer.
*   memory is **unaliased** if there is currently only one way to refer to it.

Anonymous memory is in some sense “completely under the control of the compiler” and can therefore be freely assumed to be unaliased and trusted/modified by the compiler. Unaliased memory cannot be “randomly” modified by something seemingly “unrelated” (we’ll get to what that means in the next section).

Languages can have _stricter_ or _weaker_ aliasing models. A stricter model allows the compiler to do more optimizations but puts heavier restrictions on what the programmer is allowed to do within the confines of the language. Here are some common rules, in vaguely increasing strictness:

*   Callee-saved values pushed to the stack are anonymous (return pointer, frame pointer).
*   “Scratch” values the compiler spills to the stack are anonymous.
*   A newly declared variable is unaliased until a reference is taken to it.
*   The memory returned by `malloc` is unaliased.
*   Fields of a struct do not alias eachother (bitfields are made of sadness).
*   Padding bytes are vaguely anonymous (messy because of memcpy/memset/unions/punning).
*   Immutable variables are functionally unaliased in that they can never change values.
*   In Rust, `&mut` is unaliased ([Stacked Borrows](https://plv.mpi-sws.org/rustbelt/stacked-borrows/)).
*   In C(++), `T*` and `U*` cannot alias if `T!=U` and neither is `char` ([Strict Aliasing](https://blog.regehr.org/archives/1307)).

(I cannot emphasize enough how shorthanded all of this is, the devil is extremely in the details and formally specifying these things is this subject of untold numbers of PhD theses. I am not trying to write a PhD thesis right now. Unless you literally work on a C/C++ Standard Committee or are named Ralf Jung I will not be accepting your Umm Actually’s on these definitions and terms.)

[1.2 Alias Analysis and Pointer Provenance](#alias-analysis-and-pointer-provenance)
-----------------------------------------------------------------------------------

Ok so you have some definitions for how memory can be considered “unaliased”, but as soon as you take a pointer to something, or copy a pointer, or offset a pointer… that all goes out the window, right? Like you have to assume anything can be aliased by anything else?

No! Aliasing rules are some of the most foundational parts of a language’s semantics and optimizations. If you run afoul of the language’s aliasing rules you have Undefined Behaviour and the miscompilations can be extremely brutal!

But yes, once you start faffing around with pointers things get _a lot harder_ for the compiler, memory model, and programmer. To make aliasing a useful notion once pointers start getting thrown around, memory models very quickly find the need to define two concepts:

*   Allocations
*   Pointer Provenance

_Allocations_ abstractly describe things like individual variables and heap allocations. A freshly created allocation (variable decl, malloc) is always brought into the world unaliased and therefore acts like a _sandbox_ with One True Name – there is no way to access the memory in the sandbox _except_ through the One True Name (that isn’t Undefined Behaviour).

Permission to access the allocation’s sandbox can be _delegated_ from the One True Name by deriving a new pointer from it (or anything recursively derived from it). The process of tracking this “chain of custody” from the One True Name to all of its derived pointers is _Pointer Provenance_.

From a formal memory model perspective, all accesses to an allocation must have _provenance_ tracking back to that allocation. If pointer provenance isn’t satisfied, then that means the programmer broke out of the sandbox or pulled a pointer from the aether that happened to point into some random sandbox. Either way, everything is chaos and nothing makes sense anymore if that’s allowed.

From a compiler optimization perspective, tracking provenance allows the compiler to prove that two accesses don’t alias. If two pointers are known to have different provenance, then they cannot possibly alias and you can get Good Codegen. If it ever loses track of a pointer to some memory (i.e. if pointers are passed to an opaque function) then it has put that memory/pointer in a “may be aliased” bucket. Accesses through two may-be-aliased sources have to conservatively be assumed to alias and can get Bad Codegen.

This is the fundamental trick compilers apply to all impossible problems: have a simple analysis that can answer your query with “YES”, “NO”, or “MAYBE” and then convert “MAYBE” to “YES” or “NO” based on whichever one is safer. Do these two accesses MAYBE alias? Then YES they alias. Problem Solved.

In a memory-safe language, this is all “just” an optimization scheme because the programmer can’t “break” the compiler’s analysis. But once you’re doing unsafe things (like with C or Unsafe Rust), the compiler needs you to help it out and actually follow some dang rules. Specifically, everyone agrees you _really_ shouldn’t be allowed to break out of allocation sandboxes.

This is why llvm’s [GetElementPointer (GEP)](https://llvm.org/docs/GetElementPtr.html) instruction, which computes a pointer offset, is almost always emitted by compilers with the `inbounds` keyword. The `inbounds` keyword is basically “I promise this offset won’t break the pointer out of its allocation sandbox and completely trash aliasing and provenance”. Which like, yeah all of your pointer offsets should follow that rule!

Let’s go up a level and look at rustc: any time you do `(*ptr).my_field` the compiler will emit `GEP inbounds`. Have you ever wondered why the documentation for [ptr::offset](https://doc.rust-lang.org/std/primitive.pointer.html#method.offset) and friends is so weird and complicated? Because they lower to `GEP inbounds` and need to follow its rules! [ptr::wrapping_offset](https://doc.rust-lang.org/std/primitive.pointer.html#method.wrapping_offset) is just `GEP` without the `inbounds`. And even `wrapping_offset` isn’t _actually_ allowed to break provenance:

> Compared to `offset`, this method basically delays the requirement of staying within the same allocated object: `offset` is immediate Undefined Behavior when crossing object boundaries; `wrapping_offset` produces a pointer but still leads to Undefined Behavior if a pointer is dereferenced when it is out-of-bounds of the object it is attached to.

Mea culpa, I spent years calling [CHERI](https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/) completely unshippable vaporware! I was pretty confident, but I’ll eat my hat because [ARM Morello actually built and shipped a full CHERI-based CPU](https://www.arm.com/architecture/cpu/morello). Congratulations to everyone who worked on it!

So what is CHERI? I’m not going to get into the nitty-gritty details but roughly speaking it’s a 128-bit architecture. Well actually it’s 129-bit. Well actually it’s 64-bit. _Sorry what?_

Ok so the whole Idea with CHERI is that it actually reifies and implements the “sandboxing” model from the previous section. Every pointer is tagged with extra metadata that the hardware maintains and validates. If you ever break out of your sandbox the hardware will catch it and the OS will presumably kill your process.

I don’t know the full details of the encoding or metadata, but the part we care about is that each pointer contains a compressed _slice_ (range of memory) that it is allowed to point into as well as the _actual_ address that it points to. The slice is that pointer’s sandbox, and all pointers derived from it inherit that sandbox (or less). Whenever you access some memory, the hardware just checks that the pointer is still inside its sandbox.

This metadata isn’t cheap: pointers in CHERI are 128-bits wide, but the effective address space is still at most 64-bit (I don’t know the exact upper bound, all that matters is that addresses _fit_ in 64-bit). Now 128-bit is _really_ bloated, so in C(++) CHERI actually gets help from our old nemesis [The Wobbly C Interger Hierarchy](https://gankra.github.io/blah/rust-layouts-and-abis/#the-c-integer-hierarchy).

C makes a distinction between `intptr_t` (“a pointer-sized integer”) and `ptrdiff_t`/`size_t` (“offset-sized integers”). Under CHERI, `intptr_t` is 128-bit and `ptrdiff_t`/`size_t` are 64-bit. It can do this because the address space is still only 64-bit, so anything that refers to offsets or sizes can still be 64-bit.

Ok so you might have two burning questions at this point: how on earth can this possible work if I can just scribble over a pointer and corrupt its metadata, and why did you say it’s actually 129-bit. As it turns out, those are the same question!

I find the best way to conceptualize this is to think of it like [ECC (Error Correction Code) RAM](https://en.wikipedia.org/wiki/ECC_memory). In ECC RAM, each RAM stick actually has more physically memory than it claims, because it’s transparently using that extra memory to correct or detect random bitflips. So there’s all this extra memory _somewhere_ but as far as a compiler or programmer are concerned, the memory looks perfectly normal and doesn’t have any weird extra bits.

CHERI does the same thing, but the extra 129th bit the hardware is hiding from you is a “metadata is valid” bit. You see, to properly manipulate pointers in CHERI you need to access the memory/registers containing a pointer with specific instructions for that task. If you try to manipulate them some other way (say by memcpying random bytes over it), the hardware will disable the “metadata is valid” bit. Then if you try to use it _as_ a pointer, the hardware will see your metadata can’t be trusted and fault/kill your process.

It’s friggin’ neato!

(A lot of the issues we’ll see with integrating Rust with CHERI will actually look a lot like issues with _segmented architectures_, but I have never used those so I will just be vaguely gesturing at them and handwaving. Just keep in mind that whenever I refer to CHERI, a similar argument _also_ probably applies to segmenting. So if you care about segmented architectures, you might care about CHERI too!)

Now let’s see how Rust’s current unsafe pointer APIs cause problems for all the background we’ve seen above.

Rust currently says this code is totally cool and fine:

```
// Masking off a tag someone packed into a pointer:
let mut addr = my_ptr as usize;
addr = addr & !0x1; 
let new_ptr = addr as *mut T;
*new_ptr += 10;
```

This is some pretty bog-standard code for messing with tagged pointers, what’s wrong with that?

Think about the background we just discussed. Think about Pointer Provenance. Think about CHERI.

🙀 aAAaAAaaaAAaAAAAAA 🙀

For this to _possibly_ work with Pointer Provenance and Alias Analysis, that stuff must pervasively infect all integers on the assumption that they _might_ be pointers. This is a huge pain in the neck for people who are trying to actually [formally define Rust’s memory model](https://plv.mpi-sws.org/rustbelt/stacked-borrows/), and for people who are [trying to build sanitizers for Rust that catch UB](https://github.com/rust-lang/miri). And I assure you it’s [just as much a headache for all the LLVM and C(++) people too](http://www.open-std.org/jtc1/sc22/wg14/www/docs/n2676.pdf).

For this to _possibly_ work with CHERI we need to make usize 128-bit (even though the address space is 64-bit) and always manipulate it with “pointer instructions” on the assumption that it _might_ be a pointer in the vein of intptr_t. Yes folks have tried running Rust under CHERI and [that’s exactly what they had to do](https://nw0.github.io/cheri-rust.pdf). It was, Not Good.

Unfortunately for CHERI, Rust actually _defines_ `usize` to be the same size as a pointer, even though its primary role is to be an offset/size. This is a _very_ reasonable assumption for mainstream platforms, but it runs afoul of CHERI (and segmented architectures)!

If you _don’t_ make usize 128-bit and just try to make it the 64-bit “address” portion, then `usize as *mut T` is a completely incoherent operation. Promoting an integer to a pointer (or what CHERI calls _a capability_) requires adding metadata to it. What metadata? What range is this random address possibly valid for? There is literally no way to answer that question!

Now you might be thinking “ok but pointer tagging is a super fundamental thing, are you saying we can’t do that anymore?”. Nope! You can totally still do tagging tricks, but you need to be a bit more careful about it. This is why CHERI actually [introduces a special operation](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-947.pdf#page=28):

```
void* cheri_address_set(void* capability, vaddr_t address)
```

This takes a valid pointer (capability) and an address, and creates a new pointer with the same metadata but the new address. `vaddr_t` is a new integer type that CHERI introduced which is morally equivalent to other “address-space-sized” pointers like `size_t`, `ptrdiff_t`, etc.

Hey! That operation _also_ looks really useful for provenance, doesn’t it? By associating our int-to-ptr operation with an existing pointer we are _reestablishing_ the provenance chain of custody: the new pointer is derived from the old one, and compilers and memory-models can be happy! HMMMM…

In the grand old days of Rust 1.0, we were pretty optimistic about how fast-and-loose we could be with raw pointers. Well, ok we were actually pretty rigorous about pointers by most people’s standards. We largely enforced GEP inbounds semantics, required alignment everywhere, [carved out how to work with ZSTs](https://doc.rust-lang.org/nightly/nomicon/vec/vec-zsts.html), [ensured that allocations can’t be larger than isize::MAX](https://doc.rust-lang.org/nightly/nomicon/vec/vec-alloc.html), etc.

But what we played really fast and loose on was _aliasing_ and _validity_. In Ye Olde conception of Rust, references were kinda just _conveniences_. Like yes they asserted many things, but not in a _compiler optimization_ kinda way. Just in a “this API guarantees this” kinda way. We all vaguely knew we _wanted_ the optimization-y stuff but no one had spent the energy to work that out.

These days, between [unsafe-code-guidelines](https://github.com/rust-lang/unsafe-code-guidelines), [miri](https://github.com/rust-lang/miri) and [stacked borrows](https://plv.mpi-sws.org/rustbelt/stacked-borrows/), a lot of us have now put a lot of thought into this. Miri is especially useful because it lets us “kick the tires” on actual code and check if the semantics we’re interested in are actually obeyed by real unsafe Rust code.

They Weren’t! This is why [the unsafe queue](https://rust-unofficial.github.io/too-many-lists/fifth.html) in Learn Rust With Entirely Too Many Linked Lists abruptly comes to a halt for a 4000 word delve into miri and stacked borrows! Even something as boring as a linked queue in Ye Olde Rust had confusing and busted semantics.

(For real read that chapter if you want to understand stacked borrows, I’m not rehashing it here.)

The fundamental issue is that under our modern understanding of Rust, even _creating_ a reference is making an extremely strong validity assertion and has side-effects on the “borrow stack” which in turn changes which references are considered to invalidate or not. For a reference to `T` this potentially includes:

*   The reference is aligned
*   The reference is non-null
*   The pointed-to-memory is allocated and has at least `size_of::<T>()` bytes.
*   If T has [invalid values](https://doc.rust-lang.org/nomicon/what-unsafe-does.html), the pointed-to-memory does not contain one.

The upshot of all of this is that _generally_ you should avoid mixing references and unsafe pointers. Unsafe code should _generally_ provide a safe-referency-interface at its API boundary, and then internally drop the references and try to stay in unsafe pointer land. This way you minimize the strong assertions you make about your sketchy low-level data structures’ memory.

Ok, simple enough, right?

[2.3 Offsets And Places Are A Mess](#offsets-and-places-are-a-mess)
-------------------------------------------------------------------

So you’re trying to be responsible and stay in unsafe pointer land and it’s time to offset a pointer. That’s easy, we have ptr::offset/add/sub for that! Let’s just offset to this struct’s field… uh… wait what’s that field’s offset?

Oh Rust just, doesn’t tell me that huh? Well maybe you can do something like:

Oh no wait that made a reference. Yes even if you immediately cast it to a raw pointer. How the heck do you take an address without creating a reference? Also is it actually fine for me to use a reference to initialize uninit memory? Sort of, sometimes.

This is a big confusing mess. For a long time we tried to have some kind of “5-second rule” thing where if you converted the reference to a raw pointer “fast enough” then it’s OK but that was pretty clearly untenable for a formal model (I advocated for it, it would have been nice!). So folks came up with [a proper RFC for raw addresses](https://github.com/rust-lang/rfcs/blob/master/text/2582-raw-reference-mir-operator.md) and for a long time we’ve had a hacky [addr_of macro](https://doc.rust-lang.org/stable/std/ptr/macro.addr_of.html) that lets you do this:

…yeah I hate it too.

And even that didn’t put the nail in the coffin. There was recently [a post by a very experienced rust developer](https://lucumr.pocoo.org/2022/1/30/unsafe-rust/) that basically amounted to confused frustration at the current state of affairs with doing this stuff with [uninitialized memory](https://doc.rust-lang.org/nomicon/unchecked-uninit.html). Meanwhile the _actual_ thing proposed in the RFC [has seemingly been stalled out for years](https://github.com/rust-lang/rust/issues/64490) because the Experts on this stuff are themselves [confused by the corner-cases of addr_of](https://github.com/rust-lang/unsafe-code-guidelines/issues/319).

And to make it even worse, addr_of also makes it really hard to do a thing people _still_ want which is static [offsetof](https://en.cppreference.com/w/cpp/types/offsetof).

It is my assertion that a lot of this boils down to two facts:

*   Dereferencing Pointers Is Fake Nonsense
*   [Places](https://doc.rust-lang.org/reference/expressions.html#place-expressions-and-value-expressions) Are Extremely Confusing Magic (Rust’s term for lvalues)

Like if we think about what “dereferencing” a pointer is… it’s actually nothing? Like dereferencing a pointer doesn’t actually _do_ a thing. It puts you in “place expression” mode and lets you specify an offset to subfields/indices of the pointee, and then what _actually_ happens is only specified at the end. e.g.

```
&mut (*ptr).field
```

This is certainly _familiar_ syntax but it’s genuinely also kind of magical in the exact same way autoderef is in Rust. That is to say, it makes a kind of sense and honestly you just don’t need to think about the fact that it’s happening _in safe Rust code_ because you know the compiler has your back and will help out if anything goes wrong. But in unsafe Rust code? This stuff is way too fuzzy. I literally can’t tell if the indexing is into a slice or an inline array, or if any of those `.`s is dereferencing stuff implicitly.

(Also as far as memory-model goes, there’s actually some disagreement on whether dereferencing in-and-of-itself _actually_ has no intrinsic meaning or if it does some validity assertions!)

As I said before, when you’re doing unsafe pointer stuff you want to _stay_ in that mode. That is currently _impossible_ with this place-expression design, because as soon as you deref you’re kinda in a weird twilight between safe and unsafe!

Alright and now here is where I start going off the rails and proposing wild overhauls to Rust with almost no regard for “parsing”.

[3.1 Distinguish Pointers And Addresses](#distinguish-pointers-and-addresses)
-----------------------------------------------------------------------------

The connection between `usize` and pointers needs to be completely overhauled, and I would take a chainsaw to it (using proper [editions and deprecation periods](https://doc.rust-lang.org/edition-guide/editions/index.html)).

Here’s the high level look at our tasteful chainsawing:

*   Define a distinction between a _pointer_ and an _address_
*   Redefine usizes as address-sized, which is <= pointer-sized (and usually ==)
*   Define `ptr.addr() -> usize` and `ptr.with_addr(usize) -> ptr` methods
*   Deprecate `usize as ptr` and `ptr as usize`

First off, those definitions. A pointer is still a pointer as we know it, but we now acknowledge that it points into a specific _address space_. A pointer also contains an _address_ which is conceptually an offset into this address space.

(For all major architectures _and_ CHERI there is only one address space as far as I’m concerned, but it’s potentially worth opening the door for properly talking about pointers in segmented architectures here. Although regarding x64’s TLS (Thread Local Storage) implementation as a separate address space from the perspective of a thread is probably more honest.)

A usize is large enough to contain all addresses for all address spaces on that platform. For major architectures, that means a `usize` is still pointer-sized. For CHERI, that means `usize` can (and should) be a `u64` and is equivalent to CHERI’s `vaddr_t`. To keep things tolerable I think it would be reasonable to still require that `usize`/`isize` is the same as `size_t` and `ptrdiff_t` in the target’s ABI.

(Again hopefully this generic definition is useful for segmenting, although I’ve heard nasty rumors of segmented platforms that actually decouple `size_t` and `ptrdiff_t` which is horrible and maybe still something we don’t want to support.)

As a result, someone writing _maximally portable_ Rust must now replace their assumptions:

`size_of::<usize>() == size_of::<*mut u8>()`

is now:

`size_of::<usize>() <= size_of::<*mut u8>()`

There should probably be a `cfg(target_address_size_is_pointer_size)` or something to allow people to specify software is incompatible with _weird_ platforms where the strict equality doesn’t hold.

I don’t think Rust needs to define a moral equivalent to `intptr_t`, if the new casting APIs work out as well as I hope – `*mut ()` is already `intptr_t` for most valid purposes. As far as I’m aware the `intptr_t` shenanigans that CHERI does are less “definitely good and desirable” and more “awful hacks to get old code working”. That said, people keep vaguely mentioning memory-mapped hardware as a place where this might be important, but that is outside my domain of expertise (and clearly needs special segment/provenance/capability handling _anyway_).

Next off, replacing casts with methods. All casts from raw pointers to/from integers are to be deprecated. This _primarily_ means for isize/usize but for whatever reason rust lets you do `ptr as u8` too and that is even _more_ gibberish.

The following new methods would be added:

```
addr_of!((*ptr).field)
```

Deprecating the casts may seem extreme, but as far as I’m concerned this is the exact same situation as [when we deprecated mem::uninitialized](https://gankra.github.io/blah/initialize-me-maybe/). The design of these casts is fundamentally broken under both Pointer Provenance and CHERI. Everyone needs to use a better design that actually has a coherent meaning.

Now _technically_ you could keep `ptr as usize` but I think it’s better to replace both for several reasons:

*   Getting a deprecation warning for both sides of the cast raises a big red flag to _everyone_ doing anything even vaguely dubious with a usize that they have some thinking to do.
*   You can’t hang documentation off of casts. As I hope this post demonstrates, int-ptr stuff is extremely subtle and hairy, and deserves a lot of detailed documentation!
*   `ptr as usize` is horribly clunky in practice so destroying it is honestly a mercy.
*   Straight-up symmetry/aesthetics. It’s weird to only have one!

As the documentation notes, the new with_addr method allows us to reconstitute many things:

*   What segment the address goes to (hopefully)
*   _Provenance_ for the purposes of memory models / alias analysis
*   _Metadata_ for the purposes of CHERI (but this is just a reification of provenance)

…that it! It just fixes the issue. That’s all you need to fix provenance and CHERI! (And maybe also support segmenting.)

(In reality there might need to be some more special APIs added to satisfy the existing Jank uses of ptr-int conversions, but that really needs to be shaken out on crates.io and with the community.)

> Unclear detail: is get_addr/with_addr also necessary/useful for [ARMv8.3 Pointer Authentication](https://www.qualcomm.com/media/documents/files/whitepaper-pointer-authentication-on-armv8-3.pdf)? This is a technology that [Apple ships](https://github.com/apple/llvm-project/blob/next/clang/docs/PointerAuthentication.rst) and involves some pointers getting signed/obfuscated to make it a bit harder to do memory-safety exploits. I haven’t looked into it enough to know what level of abstraction this “leaks” into. I just know about it because it shows up in minidumps and we have to [hackily try to strip it out](https://github.com/rust-minidump/rust-minidump/blob/7eed71e4075e0a81696ccc307d6ac68920de5db5/minidump-processor/src/stackwalker/arm64.rs#L252).

[3.2 Fixing Places and Offsets](#fixing-places-and-offsets)
-----------------------------------------------------------

Ok here’s a two-part combo of syntactic niceties to make it a lot easier to work with unsafe pointers. I am almost _certain_ that I’m going to run afoul of parser ambiguities somewhere here but hey this isn’t a real RFC and I get to make the rules. Maybe it works fine. Maybe it can be fixed in an edition. Let’s find out!

Hey Did You Know Rust [Never Actually](https://github.com/rust-lang/reference/pull/1149) Removed Tilde (`~`) From [The Syntax](https://doc.rust-lang.org/nightly/reference/tokens.html#punctuation)?

Did you also know that `~` was one of the things that originally drew me to messing around with Rust back in like 2014, and that I was very sad to learn that it was already being removed?

Well today I get my justice. Today I return `~` to its position of glory that is _deserved_.

Here is my grand vision that will solve all of Rust’s woes around “staying in unsafe pointer mode” and just generally dealing with offsets: If you write `my_ptr~field` (in analogy to `my_struct.field`) it always does a raw pointer offset and doesn’t change the level of indirection (but does change the pointee’s type).

Note that this is _different_ from C’s `->` in that `ptr->field` is `(*ptr).field` and therefore puts in you “place expression” mode. Nested `->`’s are actual _loads_ from memory (because you need to get the address to start the next level of offsets from). `~` will never cause an implicit load/store because it doesn’t change levels of indirection or enter “place expression” mode. It is _purely_ sugar for:

```
(*ptr).field1.field2[i].field4;     // load
(*ptr).field1.field2[i].field4 = 5; // store
&(*ptr).field1.field2[i].field4     // offset (*maybe*)
```

`ptr~field~subfield` does not need to appeal to “place expressions” and can always be done (and parsed/implemented) as piecewise application of the binary `~` operator:

```
// Ditto for `*const T`

impl<T: ?Sized> *mut T {
    /// Gets the "address" portion of the pointer.
    ///
    /// On most platforms this is a no-op, as the pointer is just an address,
    /// and is equivalent to the deprecated `ptr as usize` cast.
    ///
    /// On more complicated platforms like CHERI and segmented architectures,
    /// this may remove some important metadata. See [`with_addr`][] for
    /// details on this distinction and why it's important.
    fn addr(self) -> usize;

    /// Creates a new pointer with the given address.
    ///
    /// This replaces the deprecated `usize as ptr` cast, which had
    /// fundamentally broken semantics because it couldn't restore 
    /// *segment* and *provenance*.
    ///
    /// A pointer semantically has 3 pieces of information associated with it:
    ///
    /// * Segment: The address-space it is part of.
    /// * Provenance: An allocation (slice) that it is allowed to access.
    /// * Address: The actual address it points at.
    ///
    /// The compiler and hardware need to properly understand all 3 of these
    /// values at all times to properly execute your code.
    ///
    /// Segment and Provenance are implicitly defined by *how* a pointer is
    /// constructed and generally propagates verbatim to all derived pointers.
    /// It is therefore *impossible* to convert an address into a pointer
    /// on its own, because there is no way to know what its segment and
    /// provenance should be.
    ///
    /// By introducing a "representative" pointer into the process we can
    /// properly construct a new pointer with *its* segment and provenance,
    /// just as any other derived pointer would. This *should* be equivalent
    /// to `wrapping_offset`ting the given pointer to the new address. See the
    /// docs for `wrapping_offset` for the restrictions this applies.
    ///
    /// # Example
    ///
    /// Here is an example of how to properly use this API to mess around
    /// with tagged pointers. Here we have a tag in the lowest bit:
    ///
    /// ```rust,ignore
    /// let my_tagged_ptr: *mut T = ...;
    ///
    /// // Get the address and do whatever bit tricks we like
    /// let addr = my_tagged_ptr.addr();
    /// let has_tag = (addr & 0x1) != 0;
    /// let real_addr = addr & !0x1;
    ///
    /// // Reconstitute a pointer with the new address and use it
    /// let my_untagged_ptr = my_tagged_ptr.with_addr(real_addr);
    /// *my_untagged_ptr = ...;
    /// ```
    fn with_addr(self, addr: usize) -> Self;
}
```

Let’s look at some examples:

```
ptr.cast::<u8>().offset(field_offset).cast::<FieldTy>()
```

Yes `~[idx]` is a bit wonky but it’s _clear_ and _concise_ and that’s the most important thing. Note that this is what you would have to do in today’s Rust:

```
let ptr_field = ptr~field;
let ptr_subfield = ptr_field~subfield;
```

Or if you’re being clever and trying to leverage the fact that POD types can be initialized without `write` if your place-expression is derived from a raw pointer dereference:

```
// Some non-POD type with some fields
struct MyType {
    field1: bool,
    field2: Vec, // non-POD!!!
    field3: [u32; 4],
}

// Using ~ syntax on a raw pointer to cleanly initialize MaybeUninit
let init = unsafe {
    let mut uninit = MaybeUninit::<MyType>::uninit();
    let ptr = uninit.as_mut_ptr();

    ptr~field1.write(true);
    ptr~field2.write(vec![]);
    ptr~field3~[0].write(7);
    ptr~field3~[1].write(2);
    ptr~field3~[2].write(12);
    ptr~field3~[3].write(88);

    uninit.assume_init();
};
```

What I _really_ like about the ~ version is that:

*   It’s all postfix just like we learned is Very Good And Nice with `.await`! Just look at how nasty `addr_of!((*ptr).field2).write(vec![])` is!
    
*   Each `~` can be evaluated individually – there’s no need for the language to enter a “mode” where it’s evaluating a “place” as far as the programmer is concerned. (The compiler is free to do it that way behind the scenes, you just don’t need to know about it.)
    
*   Because you _stay_ in raw-pointer mode, it’s much less painful to reach for things like the `read` and `write` methods. This makes it just as easy to do more complicated things like `read_volatile` and doesn’t encourage you to be “clever” and lean on the fact that things happen to be POD. All `write`s is a very nice kind of _mindlessly right_.
    
*   You never have to worry about accidentally tripping over autoderef or any other thing that is nice for safe code but a huge hazard for unsafe code.
    
*   By getting rid of the `(*ptr).` “syntactic salt”, programmers are motivated to move to the nicer and more robust new syntax. Yes I _really_ think this syntax is nice! It’s certainly better than `->` in C!
    

We can also conceptually extend this syntax so it’s allowed on types and computes a const offsetof in usize bytes. Note that unlike `~` on values, this syntax can’t operate “one step at a time” and needs to be evaluated more like “path expressions”. Magic is less concerning in this context because any mistake is a compiler error. Here’s how you might use it to do more “sketchy” offsets:

```
let init = unsafe {
    let mut uninit = MaybeUninit::<MyType>::uninit();
    let ptr = uninit.as_mut_ptr();

    addr_of!((*ptr).field1).write(true);
    addr_of!((*ptr).field2).write(vec![]);
    addr_of!((*ptr).field3[0]).write(7);
    addr_of!((*ptr).field3[1]).write(2);
    addr_of!((*ptr).field3[2]).write(12);
    addr_of!((*ptr).field3[3]).write(88);

    uninit.assume_init();
};
```

I am less passionate about the const offsetof stuff but it _seems_ like it could be made to work and I know people really want that stuff.

Additional notes:

*   It should propagate `*const` vs `*mut`
*   I don’t know if it makes sense or is a good idea but maybe you could use `~` on actual references and non-references (int, struct, array, tuple…) and not just raw pointers?
    *   If so, it may be desirable to support `val~self` as a nicer postfix way to write `&mut val as *mut _` but this is messy if you support both references and non-references since that would be potentially ambiguous as to whether you want a raw-pointer-to-ref or just raw-pointer.

This is the least well-formed idea in here, but as long as we’re cleaning up raw pointers with nice and clean postfix syntax it would be _really_ nice if we also had postfix deref. Note that because of the whole “creating a reference does magic assertions” thing you _can’t_ provide something like a `deref(self) -> &T` method that actually has the same semantics as `*ptr`! Dereferencing raw pointers _must_ have first-class syntax.

Consider for instance trying to access some multiply-indirected value.

Today:

```
let init = unsafe {
    let mut uninit = MaybeUninit::<MyType>::uninit();
    let ptr = uninit.as_mut_ptr();

    (*ptr).field1 = true;
    addr_of!((*ptr).field2).write(vec![]);
    (*ptr).field3[0] = 7;
    (*ptr).field3[1] = 2;
    (*ptr).field3[2] = 12;
    (*ptr).field3[3] = 88;

    uninit.assume_init();
};
```

With offset syntax:

```
// Using ~ on a type for const offsetof (usize byte offset)
const MY_FIELD_OFFSET: usize = MyType~field1~[2];

// If you want this to be syntactically distinct,
// then we can require some amount of `::`
//
// Option A: MyType::~field~[2];
// Option B: MyType::~field::~[2];

// A pointer to some sketchy memory
// !!IMPORTANT THAT THIS IS IN BYTES!!
let ptr: *mut u8 = ...;

// We're doing evil things, so wrapping_add
let field_ptr = ptr.wrapping_add(MY_FIELD_OFFSET) as *mut FieldType;
// use field_ptr somehow...
```

With offset syntax and reads (remember, we’re staying in pointer mode, so `ptr2.read()` is loading `ptr2` from memory, so we can actually keep just using `~` syntax):

```
addr_of!((*(*(*ptr1).field1.ptr2).ptr3).field4).read()
```

With postfix deref:

```
(*(*ptr1~field1~ptr2)~ptr3)~field4.read()
```

(I think I independently came up with this `.*` syntax but I was very happy to learn that Zig [actually has it](https://ziglang.org/documentation/master/#Pointers), and `ptr.* += 1` is valid Zig syntax!)

The ambiguity issue with `.*` in Rust is that `1.` is a valid float literal, so stuff like `1. * 1.` is valid syntax and dangerously close to `1.*.1`. I certainly can imagine nasty ambiguities!

One nice thing about the `~` syntax is that because unary `*` already binds pretty weakly (which is why we need to do `(*ptr).field`), if you only need to do one deref, it’s as clean as using normal references:

So actually the more I write this section the less I’m feeling the _need_ for postfix deref, but in my heart-of-hearts I still want it.

Oh also you could imagine wanting `.&` and `.&mut` but similar syntax messes probably apply.

Jesus that was a lot.

I think about unsafe pointers in Rust a lot.

I wrote this all in one sitting and I really need dinner.

Head empty only pointers.