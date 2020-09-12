# ArrayDeque

Java里有一个叫做Stack的类，却没有叫做Queue的类（它是个接口名字）。当需要使用栈时，Java已不推荐使用Stack，而是推荐使用更高效的ArrayDeque；既然Queue只是一个接口，当需要使用队列时也就首选ArrayDeque了（次选是LinkedList）。

## 介绍

要讲栈和队列，首先要讲Deque接口。Deque的含义是“double ended queue”，即双端队列，它既可以当作栈使用，也可以当作队列使用。下表列出了Deque与Queue相对应的接口：

Queue Method | Equivalent Deque Method | 说明
-------------|-------------------------|---------------------
add(e)       | addLast(e)              | 向队尾插入元素，失败则抛出异常
offer(e)     | offerLast(e)            | 向队尾插入元素，失败则返回false
remove()     | removeFirst()           | 获取并删除队首元素，失败则抛出异常
poll()       | pollFirst()             | 获取并删除队首元素，失败则返回null
element()    | getFirst()              | 获取但不删除队首元素，失败则抛出异常
peek()       | peekFirst()             | 获取但不删除队首元素，失败则返回null

下表列出了Deque与Stack对应的接口：

Stack Method | Equivalent Deque Method | 说明
-------------|-------------------------|---------------------
push(e)      | addFirst(e)             | 向栈顶插入元素，失败则抛出异常
无           | offerFirst(e)           | 向栈顶插入元素，失败则返回false
pop()        | removeFirst()           | 获取并删除栈顶元素，失败则抛出异常
无           | pollFirst()             | 获取并删除栈顶元素，失败则返回null
peek()       | peekFirst()             | 获取但不删除栈顶元素，失败则抛出异常
无           | peekFirst()             | 获取但不删除栈顶元素，失败则返回null

上面两个表共定义了Deque的12个接口。添加，删除，取值都有两套接口，它们功能相同，区别是对失败情况的处理不同。一套接口遇到失败就会抛出异常，另一套遇到失败会返回特殊值（false或null）。除非某种实现对容量有限制，大多数情况下，添加操作是不会失败的。虽然Deque的接口有12个之多，但无非就是对容器的两端进行操作，或添加，或删除，或查看。

ArrayDeque和LinkedList是Deque的两个通用实现，由于官方更推荐使用AarryDeque用作栈和队列，本文将讲解ArrayDeque的具体实现。

从名字可以看出ArrayDeque底层通过数组实现，为了满足可以同时在数组两端插入或删除元素的需求，该数组还必须是循环的，即循环数组（circular array），也就是说数组的任何一点都可能被看作起点或者终点。ArrayDeque是非线程安全的（not thread-safe），当多个线程同时使用的时候，需要程序员手动同步；另外，该容器不允许放入null元素。

一般head指向末端第一个有效元素，tail指向首端第一个可以插入元素的空位。因为是循环数组，所以head不一定总在最后。

## 结构

```java
public class ArrayDeque<E> extends AbstractCollection<E>
                           implements Deque<E>, Cloneable, Serializable
```

### 主要字段：

```java
// 存储元素数组大小是2的幂  
transient Object[] elements;

// head指针指向当前元素并插入时由后向前移动
transient int head;

// tail指针指向下个添加元素的位置。插入由前往后
transient int tail;

// 数组的最小长度
private static final int MIN_INITIAL_CAPACITY = 8;
```

### 主要方法

#### add

```java
     /**
     * Inserts the specified element at the front of this deque.
     *
     * @param e the element to add
     * @throws NullPointerException if the specified element is null
     */
    public void addFirst(E e) {
        if (e == null)
            throw new NullPointerException();
        // 对head指针取余，如head=0时，-1&15=15,14&15=14，将head指针从数组后面开始
        // 从head=e.length-1开始
        elements[head = (head - 1) & (elements.length - 1)] = e;
        // 扩容
        if (head == tail)
            doubleCapacity();
    }

    /**
     * Inserts the specified element at the end of this deque.
     *
     * <p>This method is equivalent to {@link #add}.
     *
     * @param e the element to add
     * @throws NullPointerException if the specified element is null
     */
    public void addLast(E e) {
        if (e == null)
            throw new NullPointerException();
        // 从0开始
        elements[tail] = e;
        // 下一个tail 对tail取余0-1-2...并扩容
        if ( (tail = (tail + 1) & (elements.length - 1)) == head)
            doubleCapacity();
    }
```

注意：从上面addFirst与addLast方法看，前者head插入前移动一位，即head之前指向存在元素的位置。而后者直接插入，即tail指向下一个插入元素的位置。

空间问题是在插入之后解决的，因为tail总是指向下一个可插入的空位，也就意味着elements数组至少有一个空位，所以插入元素的时候不用考虑空间问题。

#### get and remove

只介绍poll方法，peek只是返回与这个差不多

```java
    /**
     * 移除head指针元素并指向head+1
     */
    public E pollFirst() {
        int h = head;
        @SuppressWarnings("unchecked")
        E result = (E) elements[h];
        // Element is null if deque empty
        if (result == null)
            return null;
        elements[h] = null;     // Must null out slot
        head = (h + 1) & (elements.length - 1);
        return result;
    }

    /**
     * 先移动tail-1指针移除元素
     */
    public E pollLast() {
    // tail在插入元素后移动指针，需要将tail-1指向添加的元素
        int t = (tail - 1) & (elements.length - 1);
        @SuppressWarnings("unchecked")
        E result = (E) elements[t];
        if (result == null)
            return null;
        elements[t] = null;
        tail = t;
        return result;
    }
```

#### 扩容与取余

在java.util的各种集合中经常看到各种使用 位与运算符`&` 实现取余操作。该方法必须满足一个条件，即必须为2^n - 1

```
1111
0010 &
0010 ==> 2

// 不满足2^n-1 不可取&
1011
0100 &
0000 ==> 0
```

```java
    /**
     * Allocates empty array to hold the given number of elements.
     *
     * @param numElements  the number of elements to hold
     */
    private void allocateElements(int numElements) {
        int initialCapacity = MIN_INITIAL_CAPACITY;
        // Find the best power of two to hold elements.
        // Tests "<=" because arrays aren't kept full.
        // 如果是1<<30传入进来，最后所有30位都是1，++后就为2<<31溢出，溢出就取最大值2<<30
        if (numElements >= initialCapacity) {
            initialCapacity = numElements;
            initialCapacity |= (initialCapacity >>>  1);
            initialCapacity |= (initialCapacity >>>  2);
            initialCapacity |= (initialCapacity >>>  4);
            initialCapacity |= (initialCapacity >>>  8);
            initialCapacity |= (initialCapacity >>> 16);
            initialCapacity++;
            //溢出就取最大值2<<30
            if (initialCapacity < 0)   // Too many elements, must back off
                initialCapacity >>>= 1;// Good luck allocating 2 ^ 30 elements
        }
        elements = new Object[initialCapacity];
    }
    /**
     * 仅当数组装满元素才扩大一倍
     */
    private void doubleCapacity() {
    	// 检查只有head与tail相等时才允许扩容
        assert head == tail;
        int p = head;
        int n = elements.length;
        // p的右边的元素个数
        int r = n - p; // number of elements to the right of p
        // 容量扩大一倍
        int newCapacity = n << 1;
        // 2<<31溢出
        if (newCapacity < 0)
            throw new IllegalStateException("Sorry, deque too big");
        Object[] a = new Object[newCapacity];
        // 右边head开始到原数组最后r个元素复制到新数组0开始到r-1
        System.arraycopy(elements, p, a, 0, r);
        // head左边的从0开始p个元素赋值到新数组从r开始到最后
        System.arraycopy(elements, 0, a, r, p);
        elements = a;
        head = 0;
        tail = n;
    }
    /**
     * 复制elements数组到指定数组。需要指定数组比elements足够大
     */
    private <T> T[] copyElements(T[] a) {
    	// 如果循环数组是连续的一段head在tail前:0--head--tail--e.length-1
        if (head < tail) {
            System.arraycopy(elements, head, a, 0, size());
        }
        // 循环数组不是连续的一段，tail在head前面:0--tail--head--e.length-1
        else if (head > tail) {
            int headPortionLen = elements.length - head;
            // 先复制head右边的元素head--length-1到数组a从0-headPortionLen-1
            System.arraycopy(elements, head, a, 0, headPortionLen);
            // 再复制tail左边的元素从elements的0--tail
            System.arraycopy(elements, 0, a, headPortionLen, tail);
        }
        return a;
    }
```

扩容示意图：
![](images/ArrayDeque_doubleCapacity.png)

----------

参考：

- ArrayDeque源码
- [https://github.com/CarpenterLee/JCFInternals/blob/master/markdown/4-Stack%20and%20Queue.md](https://github.com/CarpenterLee/JCFInternals/blob/master/markdown/4-Stack%20and%20Queue.md "Stack and Queue")
