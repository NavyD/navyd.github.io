---
title: "Stack Overflow in Rust"
date: 2021-10-12T10:50:30+08:00
draft: true
---

在刷leetcode时有题[552. 学生出勤记录 II](https://leetcode-cn.com/problems/student-attendance-record-ii/)，其中一个解法使用记忆化递归解决：

```rust
impl Solution {
    pub fn check_record(n: i32) -> i32 {
        const MOD: i32 = 1_000_000_007;
        const MARK: i32 = -1;
        fn backtrack(
            day: usize,
            absent_count: usize,
            late_count: usize,
            rewards: &mut Vec<Vec<Vec<i32>>>,
        ) -> i32 {
            if absent_count >= 2 || late_count >= 3 {
                return 0;
            }
            if day == 0 {
                return 1;
            }
            if rewards[day][absent_count][late_count] != MARK {
                return rewards[day][absent_count][late_count];
            }
            let pre_day = day - 1;
            let reward_count = backtrack(pre_day, absent_count + 1, 0, rewards) % MOD // absent
                + backtrack(pre_day, absent_count, late_count + 1, rewards) % MOD // late
                + backtrack(pre_day, absent_count, 0, rewards) % MOD; // present
            rewards[day][absent_count][late_count] = reward_count;
            reward_count
        }
        let n = n as usize;
        backtrack(n, 0, 0, &mut vec![vec![vec![MARK; 3]; 2]; n + 1])
    }
}

// for test
fn test<F: Fn(i32) -> i32>(f: F) {
    assert_eq!(f(2), 8);
    assert_eq!(f(1), 3);
    assert_eq!(f(11), 7077);
    assert_eq!(f(20), 2947811);
    assert_eq!(f(10101), 183236316);
}
#[test]
fn basics() {
    test(check_record);
}
```

运行上面的测试代码出现了`stack overflow`错误：

```bash
$ cargo test --package leetcode-rust --lib -- student_attendance_record_ii::tests::basics --exact --nocapture
thread 'student_attendance_record_ii::tests::basics' has overflowed its stack
fatal runtime error: stack overflow
error: test failed, to rerun pass '-p leetcode-rust --lib'
```

更神奇的是本地运行的测试问题在leetcode提交通过了，这一定是rust配置的问题，相同的解法在java上就不会出问题。在[rust Stack size](https://doc.rust-lang.org/std/thread/#stack-size)中可以使用`thread::Builder`或环境变量`RUST_MIN_STACK`配置stack size，默认的是2MB，修改后为5MB后测试通过

```bash
$ RUST_MIN_STACK=$((5*1024*1024)) cargo test --package leetcode-rust --lib -- student_attendance_record_ii::tests::basics --exact --nocapture
running 1 test
test student_attendance_record_ii::tests::basics ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 121 filtered out; finished in 0.03s
```

另外，上面的测试均使用debug模式，如果使用release测试正常通过，这就解释了leetcode为何能过

```bash
cargo test --release --package leetcode-rust --lib -- student_attendance_record_ii::tests::basics --exact --nocapture
```

## 分析

我们可以更简单的复现这种问题，推荐使用[Evcxr An evaluation context for Rust](https://github.com/google/evcxr)类似jshell,python3 shell。
在栈上定义一个数组大小分别为1MB,8MB，分别在main线程上运行时8MB会出现`stack overflow`的错误

```rust
const M: usize = 1 << 20;

// size 1B * 1M
let a = [0u8; 1*M];

// size 8B * 1M
let a = [0u64; 1*M];
```

<!-- TODO -->

参考：

* [Why I'm getting stack overflow?](https://www.reddit.com/r/rust/comments/fdwkda/why_im_getting_stack_overflow/)
* [How to set the thread stack size during compile time?](https://stackoverflow.com/a/29980945/8566831)
* [Default Rust thread stack size is 2MB #17044](https://github.com/rust-lang/rust/issues/17044#issuecomment-54713907)
