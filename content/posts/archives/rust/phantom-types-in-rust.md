---
title: "Phantom Types in Rust"
date: 2021-10-12T22:37:15+08:00
draft: true
---

转载自[phantom-types-in-rust](https://www.greyblake.com/blog/2021-10-11-phantom-types-in-rust/)

Let's say we have simple wrapper around `f64` that encodes distance in meters:

```rust
#[derive(Debug, Clone, Copy)]
struct Meter {
    value: f64
}

impl Meter {
    fn new(value: f64) -> Self {
        Self { value }
    }
}
```

In our application we want to be able to add and subtract distances, so we would implement `Add` and `Sub` traits for convenience:

```rust
use std::ops::{Add, Sub};

impl Add for Meter {
    type Output = Meter;

    fn add(self, another: Meter) -> Self::Output {
        let value = self.value + another.value;
        Meter { value }
    }
}

impl Sub for Meter {
    type Output = Meter;

    fn sub(self, another: Meter) -> Self::Output {
        let value = self.value - another.value;
        Meter { value }
    }
}
```

A quick manual test proves it works as expected:

```rust
fn main() {
    let one = Meter::new(1.0);
    let three = Meter::new(3.0);

    let four = one + three;
    dbg!(&four);

    let two = three - one;
    dbg!(&two);
}
```

Output:

```
&four = Meter { value: 4.0, }
&two = Meter { value: 2.0, }
```

But later we may decide that we need to introduce similar types: `Kilogram` to measure weight, `Liter` to measure volume, and so on. For each of the types, we have to implement the same traits again and again. Of course, we can use macros, but they must be the [last resort](https://www.youtube.com/watch?v=j0lSpNtjPM8) . So, [is there a better way?](https://www.youtube.com/watch?v=uOfTiTsSnM0)

Welcome phantom types 👻
------------------------

Phantom types are such types that are never used in runtime but help to enforce some constraints at compile time.

We could introduce a generic type `Unit<T>` and implement `Add` and `Sub` for it. Empty structs `MeterType` and `KilogramType` could be used to mark a particular unit. And we could define type aliases `Meter` and `Kilogram` for convenience:

```rust
struct Unit<T> {
    value: f64,
}

struct MeterType;
type Meter = Unit<MeterType>;

struct KilogramType;
type Kilogram = Unit<KilogramType>;
```

`MeterType` and `LiterType` are zero-sized types and have no runtime impact.

Sounds like a great idea, but the compiler is less excited than we are:

```
error[E0392]: parameter `T` is never used
  --> src/main.rs:38:13
   |
38 | struct Unit<T> {
   |             ^ unused parameter
   = help: consider removing `T`, referring to it in a field, or using a marker such as `PhantomData`
   = help: if you intended `T` to be a const parameter, use `const T: usize` instead
```

The compiler does not to like the unused generic parameter. I appreciate this. Let's add `unit_type: T` field to make the structure use that `T` type:

```rust
struct Unit<T> {
    value: f64,
    unit_type: T,
}
```

This solution seem to compile. Let's implement `new()` constructor for `Unit<T>`:

```rust
impl<T> for Unit<T> {
    fn new(value: f64) -> Self {
        Self {
            value,
            unit_type: // Oops! Which value should I use here?
        }
    }
}
```

But now we have to provide a concrete value to initialize `unit_type`. Let's be stubborn and implement `Default` trait for `MeterType` and `KilogramType`:

```rust
impl Default for MeterType {
    fn default() -> Self {
        MeterType
    }
}

impl Default for KilogramType {
    fn default() -> Self {
        KilogramType
    }
}
```

Now let's adjust `new()` to use the `default()` to set value for `unit_type`:

```rust
impl<T: Default> Unit<T> {
    fn new(value: f64) -> Self {
        Self {
            value,
            unit_type: T::default(),
        }
    }
}
```

Hooray! This compiles and we can proceed further implementing `Add` and `Sub` traits for newly born `Unit<T>` type:

```rust
impl<T: Default> Add for Unit<T> {
    type Output = Unit<T>;

    fn add(self, another: Unit<T>) -> Self::Output {
        let new_value = self.value + another.value;
        Unit::new(new_value)
    }
}

impl<T: Default> Sub for Unit<T> {
    type Output = Unit<T>;

    fn sub(self, another: Unit<T>) -> Self::Output {
        let new_value = self.value - another.value;
        Unit::new(new_value)
    }
}
```

Now let us test it. We still can add meters as we could before:

```rust
fn main() {
    let one_meter = Meter::new(1.0);
    let two_meters = one_meter + one_meter;
    dbg!(&two_meters);
}
```

Output:

```
&two_meters = Unit { value: 2.0, unit_type: MeterType }
```

But the most important, the compiler does not allow us to mix meters and kilograms now:

```rust
fn main() {
    let one_meter = Meter::new(1.0);
    let two_kilograms = Kilogram::new(2.0);
    let god_knows_what = one_meter + two_kilograms;
}
```

Error message:

```
--> src/main.rs:93:38
   |
93 |     let god_knows_what = one_meter + two_kilograms;
   |                                      ^^^^^^^^^^^^^ expected struct `MeterType`, found struct `KilogramType`
   |
   = note: expected struct `Unit<MeterType>`
              found struct `Unit<KilogramType>`
```

Looks good. Are we done? Not yet!

Hello PhantomData
-----------------

The problem above could be solved slightly easier with help of [PhantomData](https://doc.rust-lang.org/std/marker/struct.PhantomData.html) from the standard library.

Actually, the compiler already gave us a hint, when we introduced `Unit<T>` suggesting to use `PhantomData`:

```
help: consider removing `T`, referring to it in a field, or using a
      marker such as `PhantomData`
```

The documentation defines PhantomData as:

> Zero-sized type used to mark things that “act like” they own a T.

And what is also relevant for us:

> Though they both have scary names, PhantomData and ‘phantom types’ are related, but not identical. A phantom type parameter is simply a type parameter which is never used. In Rust, this often causes the compiler to complain, and the solution is to add a “dummy” use by way of PhantomData.

Indeed, all that we did before was the "dummy" use of the phantom type `T`. Let's use `PhantomData` for this purpose now and adjust `Unit<T>` and other code accordingly:

```rust
use std::marker::PhantomData;

#[derive(Debug, Clone, Copy)]
struct Unit<T> {
    value: f64,
    unit_type: PhantomData<T>,
}

impl<T> Unit<T> {
    fn new(value: f64) -> Self {
        Self {
            value,
            unit_type: PhantomData,
        }
    }
}
```

You can see the [full code example in playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2018&gist=e5438101bfb82eececf25c98fdf61ec0) .

PhantomData gives us at least 2 benefits:

* We can use `PhantomData` to initialize `unit_type` field. This means that `MeterType` and `KilogramType` do not have to implement `Default` anymore.
* With `PhantomData<T>` we communicate explicitly the purpose of the type parameter to other developers.

That is it for now. This was a little practical introduction to _phantom types_ with Rust. Thank you for reading.

[Dicussion on reddit.](https://www.reddit.com/r/rust/comments/q5r9uy/phantom_types_in_rust/)
