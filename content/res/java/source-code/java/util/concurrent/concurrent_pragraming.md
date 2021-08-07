## 线程安全性

编写并发程序时

- 先使代码正确运行，再提高代码速度
- 线程安全的类可通过  面向对象的设计、不可修改性、不变性规范 帮助实现
- 在类中通常定义不变性条件约束对象状态（如变量的范围），定义后验条件描述对象操作的结果
- 尽可能使用已有的线程安全对象管理类的状态
- 内置锁的锁对象应该使用私有构造锁，不推荐使用默认`this`作为锁对象。减少JVM在对象大小和加锁性能之间的权衡

```java
    private final Object lock = new Object();
    
    public void test() {
        // 使用私有构造锁作为监视对象
        synchronized (lock) {
            // do sth
        }
//        // 不应该使用默认当前对象作为锁对象
//        synchronized (this) {
//            // do sth
//        }
    }
```

- 合理缩小同步块的范围以提高性能。判断范围需要考虑安全性，简单性，性能
- 无法快速完成的操作（如长时间的计算，网络I/O等）不要持有锁











线程安全性：当多个线程访问某个类时，该类始终都能表现出正确的行为

竟态条件（Race Condition）：当某个计算的正确性由于不恰当的线程执行时序而出现不正确的结果

- 先检查后执行（Check-Then-Act）

可以使用同步避免竟态条件的发生



数据竞争（Data Race）：在访问共享的非final类型的域时没有采用同步进行协同就会出现数据竞争

复合操作必须以原子方式保证线程安全性

可重入内置锁，锁的操作粒度时线程，而不是调用（POSIX以调用为粒度）

## 线程的共享

关键字`synchronized`可用于实现原子性和内存可见性

失效数据，在缺乏同步时可能产生错误结果的一种情况

失效数据可能不会同时出现：一个线程可能获取到某个变量的最新值，而另一个线程则获取到该变量的失效值



可使用volatile声明或锁保护



volatile变量不会被重排序

编写并发程序时

- 对于非volatile 64位数值变量(double,long)的读写操作在不同线程操作时需要***使用关键字volatile或加锁保护***，避免读取到*随机值*。其他类型的变量至少可以读取到*失效值*，不可能读取到随机值

**非原子的64位操作(double,long)**被分解为两个32位操作，读写操作在不同的线程执行时可能会读取到某个值的高32位和另一个值的低32位，即64位变量可能被读取到随机值（而不像其他类型获取的为失效值）。而其他类型在读写时均为原子操作

- volatile 类型的变量不会被重排序优化，只能保证内存可见性，通常用作某状态的标志。
- 注意不要使对象内部可变状态和this引用的溢出，常见为在构造函数中启动一个线程，不应该在构造函数中立即启动一个线程


下面是错误的样例：

```java
// 对象内部可变状态 溢出
class PublishEscape {
    private String[] states = new String[] {"a", "ab"};
    // 使得内部可变状态的数组溢出，导致数组可能随时被更改
    public String[] getStates() {
        return states;
    }
}

// this溢出的样例
class ThisEscape {
    private int count;
    // 
    public ThisEscape(EventSource source) {
        // 外部线程可能随时会触发EventSource注册对象EventListener.onEvent()的调用
        source.registerListener(new EventListener() {
            @Override
            public void onEvent(Event e) {
                // 向外发布了未构造完成的this实例
                doSomething(e);
            }
        });
        // 在注册后才初始化，可能导致外部线程调用doSomething()时count还未完成初始化
        count = 111;
    }
    void doSomething(Event e) {
        System.out.println(count);
    }
}
```

- 线程封闭即在单线程中访问数据可以避免同步。常用的线程封闭技术有栈封闭，ThreadLocal类。

- 使用不可变对象避免同步，通常配合volatile发布不可变对象。创建不可变对象的条件：

  - 对象创建后状态不能被修改（即不向外提供修改对象状态的方法）
  - 对象的所有域类型都是final（final域保证安全初始化）
  - 对象是正确创建的（没有this引用溢出）

- 安全发布可变对象和事实不可变对象使其对其他线程可见，有以下方式：
  - 在静态初始化函数中初始化对象引用。静态引用将由JVM保持线程安全

  ```java
  public class ConcurrentTest {
      // 由jvm保证线程安全 (非final也允许)
      private final static String s;
      static {
          s = "test static field";
  //        System.out.println(s);
      }
  }
  ```

  - 保存到volatile域或AtomicReference对象中
  - 保存到某个正确构造对象的final域中
  - 保存到由锁保护的域中。

  通常将对象保存在线程安全容器中，其他线程可以看到该对象，但是该对象中的状态是否可见仍然需要该对象负责


可变对象必须是线程安全的

## 对象的组合



- 设计线程安全的类，具体设计还是慢慢来。。。
- 实例封闭，将数据封装到对象内部，将数据的访问限制限制在对象的方法上



























