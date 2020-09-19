# PriorityQueue

一个基于优先级堆的无界优先级队列。

## 二叉堆

二叉堆(The binary heap)数据结构能够有效的支持基本的优先队列操作。key存储在一个数组中，其中每个key大于(或等于)指定的两个位置及以上的key

如果key节点比两个key子节点（如果有）大或等于表示这个二叉树是堆有序的。（子节点间无序）

![](../../../assets/images/5a6aad91-3f5b-4953-b2b2-2712973198d0.png)

### 位置

二叉堆使用完全二叉树在数组中实现，堆中节点的位置可以用数组下标很方便的表示：

#### 数组下标1开始

![](../../../assets/images/32fbdbf9-4559-45e5-8f87-ff07ffce6620.png)

一个节点的父节点：`k/2` 向下取整

一个节点的两个子节点：左子节点`2*k`  右子节点`2*k+1`。

#### 数组下标0开始

父节点：`(k-1)/2` 向下取整

左子节点：`2*k+1`

右子节点：`2*(k+1)` 即 `(2*k+1)+1`

最后一个父节点（只有存在子节点）：`(size/2)-1`

***PriorityQueue为下标0开始***

### 有序化

#### 插入 

当一个key被添加到有序的二叉堆时，此时会破坏堆的有序性，需要交换key使堆有序。假设使用最大优先队列即父节点大于或等于子节点

##### 上浮（siftUp）

![](../../../assets/images/5fd5dedd-8459-414c-ab9e-9914ecdf4923.png)

过程很简单，即比较key与父节点p位置为`(k-1)/2`的大小：（针对最大优先队列，如果是最小优先，颠倒符号即可）

- 如果key>p就交换两者的位置并与新的父节点继续比较
- 如果key<=p排序完成

##### siftUp源码

下面是PriorityQueue的源码，注意是使用最小优先队列，如果时最大优先队列，只需要更该为`if (key.compareTo((E) e) <= 0)`

```java
// 使用指定位置k的节点x向上使堆有序
@SuppressWarnings("unchecked")
private void siftUpComparable(int k, E x) {
    Comparable<? super E> key = (Comparable<? super E>) x;
    // 找到key在堆中的位置  当key的位置k是根节点位置0时终止
    while (k > 0) {
        // k位置的父节点位置
        int parent = (k - 1) >>> 1;
        Object e = queue[parent];
        // 如果key比父节点大或相等时 此时堆有序，不用交换了
        if (key.compareTo((E) e) >= 0)
            break;
        // 将父节点移动到key的位置  交换key与父节点位置
        queue[k] = e;
        // key位置变为父节点位置
        k = parent;
    }
    // 找到key在堆中的位置
    queue[k] = key;
}
```

#### 移除

在堆中移除后，与二叉树的删除使用左右子树的最值子节点替换类似，对移除位置使用堆数组最后位置元素替换到移除位置上，然后重新平衡二叉堆。

假设使用最大优先队列即父节点大于或等于子节点

##### 下沉（siftDown）

当数组最后一个元素被替换到删除位置时，这个叶子节点元素key必定小于删除位置的父节点p，所以需要与较大的子节点child比较

![](../../../assets/images/6542b390-b72e-459a-af2f-afaad81b52f9.png)

- 如果节点key < 较大的子节点child，交换key与child的位置，并继续与新的较大子节点比较
- 如果节点key >= 较大的子节点child，完成当前堆有序
- 如果节点key交换到了叶子节点`k<half`即堆中第一个叶子节点为`half=(size/2)`（数组下标从0开始 1也一样），此时不再需要向下比较non-leaf为`(size/2) - 1`

##### siftDown源码

下面是PriorityQueue的源码（最小优先队列为例，如果是最大优先队列需要交换符号）

在向下筛选时，叶子节点不需要再向下比较筛选，所以比较完最后一个父节点size/2 -1后`(size/2)-1 < size/2）`，退出循环

```java
// 将指定元素在堆中位置为k的向下使堆有序
@SuppressWarnings("unchecked")
private void siftDownComparable(int k, E x) {
    Comparable<? super E> key = (Comparable<? super E>)x;
    //表示队列中最后一个元素的父节点的下一个节点如：4号左右分别9.10下标子节点。half=size=11 /2=5节点;
    int half = size >>> 1;        // loop while a non-leaf
    // 将指定位置节点循环到最后一个父节点(size/2)-1时为止，叶子节点不需要向下有序了
    while (k < half) {
        // k的左子节点
        int child = (k << 1) + 1; // assume left child is least
        Object c = queue[child];
        int right = child + 1;
        // 取小的子节点
        // 如果右子节点存在且比左子节点小就将右子节点更新为小的节点
        if (right < size &&
            ((Comparable<? super E>) c).compareTo((E) queue[right]) > 0)
            c = queue[child = right];
        // 如果key比子节点小或等于就退出
        if (key.compareTo((E) c) <= 0)
            break;
        // 交换位置
        queue[k] = c;
        k = child;
    }
    queue[k] = key;
}
```

#### 堆有序构造

如何使无序数组堆有序化，对于只有3个节点堆，只要对根节点siftDown，将较大的子节点交换上来，此时这个堆有序。

如果将数组看作一个个子堆，从有序子堆构造更大的子堆也只要对大子堆根节点siftDown较大的子节点交换上来，就使得整个堆有序了

![](../../../assets/images/b49a5c19-cc6c-407b-91ec-4a8fc7884008.png)

##### heapify源码

```java
// 将一个无序堆从最后的父节点开始向下筛选 直到根节点 使堆有序
@SuppressWarnings("unchecked")
private void heapify() {
    // 从最后一个父节点(size/2)-1开始直到根节点0 进行向下筛选操作
    for (int i = (size >>> 1) - 1; i >= 0; i--)
        siftDown(i, (E) queue[i]);
}
```

##### 堆排序

堆构造不能使堆数组下标有序，只有根节点是最大，左右子节点顺序不定，如果能将最大的根节点放到数组最后，下一个第二大节点放到数组倒数第二，如此就可有序

可以用与根交换上来的数组最后节点使重新对根节点构造即heapify siftDown，使新根节点在重新变成最大的（排除之前最大的）

```
    3           2               1
   / \  =>     / \      =>     / \
  1   2       1   3           2   3
```

```java
void headSort(int[] a) {
    for (int i = (size >>> 1) - 1; i >= 0; i--)
        siftDown(i, (E) queue[i]);
    // todo
}
```

## 构造器

构造器需要对堆数组和可能指定的比较器comparator初始化，还有如果使用集合初始化PriorityQueue时需要考虑集合是否有序。

下面使用两个典型的构造器说明，其他的构造器调用或调用相同的方法

### 一般初始化

优先队列创建的堆数组最小为1，默认构造器创建的大小为1，在容量不够时自动扩容

```java
public PriorityQueue(int initialCapacity,
                        Comparator<? super E> comparator) {
    // Note: This restriction of at least one is not actually needed,
    // but continues for 1.5 compatibility
    //至少容量为1是为了兼容性
    if (initialCapacity < 1)
        throw new IllegalArgumentException();
    this.queue = new Object[initialCapacity];
    this.comparator = comparator;
}
```

### 集合初始化

通过集合初始化时需要考虑原来集合是否有序，如果原来集合有序，即保证堆有序，而下标0的元素一定是最值。

```java
// 根据指定集合的元素创建优先队列，如果指定的collection是SortedSet或优先队列，
// 则使用相同的顺序排序 否则使用自然顺序
@SuppressWarnings("unchecked")
public PriorityQueue(Collection<? extends E> c) {
    // 如果是SortedSet
    if (c instanceof SortedSet<?>) {
        SortedSet<? extends E> ss = (SortedSet<? extends E>) c;
        this.comparator = (Comparator<? super E>) ss.comparator();
        // 从集合中初始化到堆数组中 检查集合元素是否存在null 由于本身是有序的 queue[0]一定是最值 不需要使堆完全有序
        initElementsFromCollection(ss);
    }
    // 如果是优先队列
    else if (c instanceof PriorityQueue<?>) {
        PriorityQueue<? extends E> pq = (PriorityQueue<? extends E>) c;
        this.comparator = (Comparator<? super E>) pq.comparator();
        // 直接使用PriorityQueue.toArray的数组 堆完整有序 
        initFromPriorityQueue(pq);
    }
    else {
        this.comparator = null;
        // 将指定的集合添加到priorityqueue中并使堆有序
        initFromCollection(c);
    }
}

// 从指定集合Collection中 初始化堆数组  此时堆数组无序
private void initElementsFromCollection(Collection<? extends E> c) {
    Object[] a = c.toArray();
    // If c.toArray incorrectly doesn't return Object[], copy it.
    // 保证底层数组queue为Object[]类型
    if (a.getClass() != Object[].class)
        a = Arrays.copyOf(a, a.length, Object[].class);
    int len = a.length;
    // 如果有比较器 扫描容器数组中元素不含null元素
    if (len == 1 || this.comparator != null)
        for (int i = 0; i < len; i++)
            if (a[i] == null)
                throw new NullPointerException();
    this.queue = a;
    this.size = a.length;
}

/**
 * Initializes queue array with elements from the given Collection.
 *
 * @param c the collection
 */
// 将指定的集合添加到priorityqueue中并使堆有序
private void initFromCollection(Collection<? extends E> c) {
    // 将集合元素初始化到优先队列queue中
    initElementsFromCollection(c);
    // 使堆有序 
    heapify();
}

// 如果是PriorityQueue就直接使用toArray的数组 否则调用initFromCollection
private void initFromPriorityQueue(PriorityQueue<? extends E> c) {
    if (c.getClass() == PriorityQueue.class) {
        this.queue = c.toArray();
        this.size = c.size();
    } else {
        initFromCollection(c);
    }
}
```

### 注意

- 优先队列创建的堆数组最小为1，默认构造器创建的大小为11，在容量不够时自动扩容
- 通过集合初始化时需要考虑原来集合是否有序，如果原来集合有序，即保证堆有序，而下标0的元素一定是最值。

下面使用一个有序集合构造为优先队列的示例说明 有序数组本就堆有序

```java
static void constructoraddAllTest() {
    SortedSet<Integer> set = new TreeSet<>();
    set.addAll(Arrays.asList(1, 3, 6, 7, 9, 12, 15));
    PriorityQueue<Integer> queue = new PriorityQueue<Integer>(set);
    System.out.println("before:" + Arrays.toString(queue.queue));
    System.out.println("after:");
    while (queue.poll() != null) {
        System.out.println(Arrays.toString(queue.queue));
    }
}
/*输出：
before:[1, 3, 6, 7, 9, 12, 15]
after:
[3, 7, 6, 15, 9, 12, null]
[6, 7, 12, 15, 9, null, null]
[7, 9, 12, 15, null, null, null]
[9, 15, 12, null, null, null, null]
[12, 15, null, null, null, null, null]
[15, null, null, null, null, null, null]
[null, null, null, null, null, null, null]
*/
```

下面是模拟堆数组第一次出队的步骤：

```
经过集合构造器的堆数组：	[1, 3, 6, 7, 9, 12, 15]

							1				<--出队
					3				6
				7		9		12		15	<--到堆顶替换
			--------------------------------	
							15				<--用数组最后元素替换
					3				6
				7		9		12		
			--------------------------------
							3
					15				6		<--下沉　取子节点中小的交换
				7		9		12
			--------------------------------
							3
					7				6
				15		9		12			<--完成下沉　
			--------------------------------
		一次出队后堆数组：	[3, 7, 6, 15, 9, 12, null]		
```

- 通过构造器构造的堆数组一定时堆有序的。不存在在插入删除时才有序，如果一开始堆数组不保证顺序，插入仅下沉和删除仅上浮不可能保证队头是最值了

## 扩容

```java
    /**
     * Increases the capacity of the array.
     *
     * @param minCapacity the desired minimum capacity
     */
    private void grow(int minCapacity) {
        // 旧数组容量
        int oldCapacity = queue.length;
        // Double size if small; else grow by 50%
        // 如果数组过小(<64)就扩大两倍，否则扩大一半50%
        int newCapacity = oldCapacity + ((oldCapacity < 64) ?
                                         (oldCapacity + 2) :
                                         (oldCapacity >> 1));
        // overflow-conscious code
        // 如果增加50%后超过最大容量，没有溢出就使用int最大或最大容量值
        if (newCapacity - MAX_ARRAY_SIZE > 0)
            newCapacity = hugeCapacity(minCapacity);
        // 复制到新数组长度为newCapaciry
        queue = Arrays.copyOf(queue, newCapacity);
    }

    private static int hugeCapacity(int minCapacity) {
        if (minCapacity < 0) // overflow
            throw new OutOfMemoryError();
        return (minCapacity > MAX_ARRAY_SIZE) ?
            Integer.MAX_VALUE :
            MAX_ARRAY_SIZE;
    }
```

### 注意

- PriorityQueue的扩容比较简单，当数组较小时(<64)扩大为数组的两倍，否则将扩大50%


## 队列Queue

### 插入

- boolean add(E e)

```java
    /**
     * Inserts the specified element into this priority queue.
     *
     * @return {@code true} (as specified by {@link Collection#add})
     * @throws ClassCastException if the specified element cannot be
     *         compared with elements currently in this priority queue
     *         according to the priority queue's ordering
     * @throws NullPointerException if the specified element is null
     */
    public boolean add(E e) {
        return offer(e);
    }
```

- boolean offer(E e)

```java
    /**
     * Inserts the specified element into this priority queue.
     *
     * @return {@code true} (as specified by {@link Queue#offer})
     * @throws ClassCastException if the specified element cannot be
     *         compared with elements currently in this priority queue
     *         according to the priority queue's ordering
     * @throws NullPointerException if the specified element is null
     */
    public boolean offer(E e) {
        // 不允许插入null元素
        if (e == null)
            throw new NullPointerException();
        modCount++;
        int i = size;
        // 如果堆数组已满  执行扩容操作
        if (i >= queue.length)
            // i + 1用于判断是否溢出， 对于一般的扩容容量没有影响，当容量达到int和vm的限制时才有影响
            grow(i + 1);
        size = i + 1;
        // 插入第一个元素
        if (i == 0)
            queue[0] = e;
        // 插入数组已有元素最后然后向上有序，i为最新位置
        else
            siftUp(i, e);
        return true;
    }
```

#### 注意

- 优先队列不允许插入null元素
- 优先队列先执行扩容操作才将元素插入新数组。即在扩容前堆数组可能装满元素
- 插入新元素后需要在堆向上筛选使堆有序

### 移除

- E remove()

由抽象类AbstractQueue提供，调用poll()方法判断返回值，如果是null就抛出异常

```java
    /**
     * Retrieves and removes the head of this queue.  This method differs
     * from {@link #poll poll} only in that it throws an exception if this
     * queue is empty.
     *
     * <p>This implementation returns the result of <tt>poll</tt>
     * unless the queue is empty.
     *
     * @return the head of this queue
     * @throws NoSuchElementException if this queue is empty
     */
    public E remove() {
        E x = poll();
        if (x != null)
            return x;
        else
            throw new NoSuchElementException();
    }
```

- E poll()

```java
    // 移除并返回队头元素。如果队列为空将返回null
    @SuppressWarnings("unchecked")
    public E poll() {
        // 队列为空 返回null
        if (size == 0)
            return null;
        // 最后一个元素位置
        int s = --size;
        modCount++;
        // 队头 最值元素
        E result = (E) queue[0];
        // 使用堆数组中最后一个元素替换队头元素  然后下沉使堆有序
        E x = (E) queue[s];
        // 删除原最后位置元素
        queue[s] = null;
        // 如果s不是数组0号元素 即数组只有一个元素s 就将新的根节点s下沉有序
        if (s != 0)
            siftDown(0, x);
        return result;
    }
```

### 检查

- E element()

由抽象类AbstractQueue提供，调用peek()方法判断返回值，如果是null就抛出异常

- E peek()

```java
     // 返回但不移除 队头元素
    @SuppressWarnings("unchecked")
    public E peek() {
        return (size == 0) ? null : (E) queue[0];
    }
```

### 注意

- 当PriorityQueue作为队列时，堆数组一定时堆有序的，因为队列仅对队头操作，无论删除还是插入都能保证堆有序

## 集合Collection

### 插入

- boolean add(E e)

与Queue的api为同一个，在上面有说明，底层实现为调用offer方法

- boolean addAll(Collection<? extends E> c)

由抽象类AbstractQueue提供，不允许将queue自己作为参数添加到queue中否则将抛出异常。遍历集合c将每个元素添加到queue中

### 移除

- void clear()

```java
    /**
     * Removes all of the elements from this priority queue.
     * The queue will be empty after this call returns.
     */
    public void clear() {
        modCount++;
        // 遍历将堆数组所有元素位置置为null
        for (int i = 0; i < size; i++)
            queue[i] = null;
        size = 0;
    }
```

- boolean remove(Object o)

```java
    /**
     * Removes a single instance of the specified element from this queue,
     * if it is present.  More formally, removes an element {@code e} such
     * that {@code o.equals(e)}, if this queue contains one or more such
     * elements.  Returns {@code true} if and only if this queue contained
     * the specified element (or equivalently, if this queue changed as a
     * result of the call).
     *
     * @param o element to be removed from this queue, if present
     * @return {@code true} if this queue changed as a result of the call
     */
	// 移除队列中的指定对象。如果队列中存在多个，将不保证删除的是哪一个
    public boolean remove(Object o) {
    	// 获取元素下标
        int i = indexOf(o);
        // 当前队列不包含该对象o
        if (i == -1)
            return false;
        else {
        	// 删除这个下标元素
            removeAt(i);
            return true;
        }
    }
```

- boolean removeAll(Collection<?> c)

由抽象类AbstractCollection提供，通过迭代器在迭代中it.remove()删除在队列中指定对象

- boolean retainAll(Collection<?> c)

由抽象类AbstractCollection提供，与removeAll类似，仅改变contains的判断

#### 私有实现

```java
    /**
     * Removes the ith element from queue.
     *
     * Normally this method leaves the elements at up to i-1,
     * inclusive, untouched.  Under these circumstances, it returns
     * null.  Occasionally偶尔, in order to maintain the heap invariant,
     * it must swap a later element of the list with one earlier than
     * i.  Under these circumstances, this method returns the element
     * that was previously at the end of the list and is now at some
     * position before i. This fact is used by iterator.remove so as to
     * avoid missing traversing elements.
     */
    // 移除数组中指定位置的元素 返回null表示正常删除成功。否则表示迭代异常，返回丢失的元素
    @SuppressWarnings("unchecked")
    private E removeAt(int i) {
        // assert i >= 0 && i < size;
        modCount++;
        // 最后元素的下标
        int s = --size;
        // i就是最后元素
        if (s == i) // removed last element
            queue[i] = null;
        else {
        	// 最后元素
            E moved = (E) queue[s];
            // 删除最后元素
            queue[s] = null;
            // 等价于将最后元素移动到删除元素位置，将其下沉有序化
            siftDown(i, moved);
            // 当前节点无法下沉 表示最后元素i比小的子节点更小（默认最小堆）
            if (queue[i] == moved) {
                // 将当前节点上浮
                siftUp(i, moved);
                // 如果当前节点能够上浮 表示数组最后元素i比父节点小
                if (queue[i] != moved)  {
                    /*
                     * 对于迭代器来说是致命的 无法保证顺序，因为已经遍历过的位置被更新了
                     * 说明之前遍历的顺序是错误的 即返回该元素遍历 由于移除的关系，最后元素i
                     * 已经不会被获取，所以提前返回该元素 
                     */
                    return moved;
                }
            }
        }
        return null;
    }
```

#### 注意

- 移除堆数组中的**除叶子节点外的元素**都只需要使用堆数组最后一个元素替换并下沉使堆有序，由于堆数组正常情况下是有序的，所以只需要下沉即可。
- 如果**删除位置为叶子节点位置**，由于不同父节点的大小无法确定，在最小堆中，存在叶子节点比其他的父节点更小的情况，此时，如果将该叶子节点替换到合适的父节点下，无法下沉，但能上浮即比父节点小。

注意这种情况非常小，需要满足替换元素即数组最后元素小于删除元素的父节点，此时需要上浮操作

```
							1				
					6				3
删除12-->		12			15		7		4	<--最后元素用于替换
			-------------------------------

							1				
					6				3
需要上浮-->		4		15		7
			-------------------------------
							1				
					4				3
   完成	 	6		15		7
			-------------------------------
```

- 关于removeAt()方法就是由于上述特殊情况的删除才会返回一个特殊值，导致遍历删除时无法保证顺序。removeAt返回null表示正常删除成功，返回一个值表示上浮更新了堆的顺序，删除操作成功

对于迭代器来说是致命的 无法保证顺序，因为已经遍历过的位置被更新了说明之前遍历的顺序是错误的 即返回该元素遍历 由于移除的关系，最后元素i已经不会被获取，所以提前返回该元素 

### 查询

- boolean contains(Object o) 

```java
    /**
     * Returns {@code true} if this queue contains the specified element.
     * More formally, returns {@code true} if and only if this queue contains
     * at least one element {@code e} such that {@code o.equals(e)}.
     *
     * @param o object to be checked for containment in this queue
     * @return {@code true} if this queue contains the specified element
     */
    public boolean contains(Object o) {
        return indexOf(o) != -1;
    }

    // 获取元素o在堆数组中的下标，找不到就返回-1 由于按照堆数组遍历，无法保证元素顺序遍历
	private int indexOf(Object o) {
		if (o != null) {
			for (int i = 0; i < size; i++)
				if (o.equals(queue[i]))
					return i;
		}
		// priorityqueue不允许null，传入null表示不存在直接返回-1
		return -1;
	}
```

- boolean containsAll(Collection<?> c)

由抽象类AbstractColleciton提供，通过集合c迭代中调用contains判断每个元素是否包含在queue中

- boolean isEmpty()

由抽象类AbstractColleciton提供，判断size() == 0

- int size()

```java
    public int size() {
        return size;
    }
```

### 比较和哈希

PriorityQueue未定义equals和hashCode方法，使用Object默认方法

`Queue` 实现通常未定义 `equals` 和 `hashCode` 方法的基于元素的版本，而是从 `Object` 类继承了基于身份的版本，因为对于具有相同元素但有不同排序属性的队列而言，基于元素的相等性并非总是定义良好的。

### 迭代器

- Iterator<E> iterator()

```java
    /**
     * Returns an iterator over the elements in this queue. The iterator
     * does not return the elements in any particular order.
     *
     * @return an iterator over the elements in this queue
     */
    public Iterator<E> iterator() {
        return new Itr();
    }

    private final class Itr implements Iterator<E> {
        /**
         * Index (into queue array) of element to be returned by
         * subsequent call to next.
         */
        // 下一个调用返回的元素下标
        private int cursor = 0;

        /**
         * Index of element returned by most recent call to next,
         * unless that element came from the forgetMeNot list.
         * Set to -1 if element is deleted by a call to remove.
         */
        private int lastRet = -1;

        /**
         * A queue of elements that were moved from the unvisited portion of
         * the heap into the visited portion as a result of "unlucky" element
         * removals during the iteration.  (Unlucky element removals are those
         * that require a siftup instead of a siftdown.)  We must visit all of
         * the elements in this list to complete the iteration.  We do this
         * after we've completed the "normal" iteration.
         *
         * We expect that most iterations, even those involving removals,
         * will not need to store elements in this field.
         */
        /*
         * 由于在迭代器中删除堆数组中的某个元素，在使用堆数组中最后一个元素替换时,该元素比删除元素
         * 的父节点更小（默认最小堆），会使该元素上浮(siftUp)导致该元素替换到已经遍历过的位置，
         * 此时使用deque存储该元素并在最后再遍历
         * 
         */
        private ArrayDeque<E> forgetMeNot = null;

        /**
         * Element returned by the most recent call to next iff that
         * element was drawn from the forgetMeNot list.
         */
        // 在遍历forgetMeNot时保存最近访问的元素
        private E lastRetElt = null;

        /**
         * The modCount value that the iterator believes that the backing
         * Queue should have.  If this expectation is violated, the iterator
         * has detected concurrent modification.
         */
        private int expectedModCount = modCount;

        public boolean hasNext() {
            return cursor < size ||
                (forgetMeNot != null && !forgetMeNot.isEmpty());
        }

        @SuppressWarnings("unchecked")
        public E next() {
            if (expectedModCount != modCount)
                throw new ConcurrentModificationException();
            // 以堆数组的顺序 返回下一个元素 即迭代器不保证优先队列的顺序
            if (cursor < size)
                return (E) queue[lastRet = cursor++];
            // 如果有unlucky元素 就遍历
            if (forgetMeNot != null) {
                lastRet = -1;
                lastRetElt = forgetMeNot.poll();
                if (lastRetElt != null)
                    return lastRetElt;
            }
            // 如果cursor >= size或 forgetmenot为空返回null
            throw new NoSuchElementException();
        }

        public void remove() {
            if (expectedModCount != modCount)
                throw new ConcurrentModificationException();
            // 正常next后删除
            if (lastRet != -1) {
                // 删除最近的访问元素  接受可能的unlucky元素
                E moved = PriorityQueue.this.removeAt(lastRet);
                lastRet = -1;
                // 删除正常 无unlucky元素
                if (moved == null)
                    cursor--;
                // 存在unlucky元素 添加进入forgetNot队列
                else {
                    if (forgetMeNot == null)
                        forgetMeNot = new ArrayDeque<>();
                    forgetMeNot.add(moved);
                }
            }
            // 如果是在遍历forgetMeNot时调用remove
            else if (lastRetElt != null) {
                // 删除最近遍历的forgetMeNot的元素
                PriorityQueue.this.removeEq(lastRetElt);
                lastRetElt = null;
            } else {
                throw new IllegalStateException();
            }
            expectedModCount = modCount;
        }
    }
```

#### 注意

- PriorityQueue的迭代器***不保证顺序遍历*** ，在需要顺序遍历时请使用`Arrays.sort(pq.toArray())`
- 迭代器不保证顺序遍历在实现中有两点：

1.迭代器是在堆数组中一个个遍历，无法保证优先队列的顺序；
2.由于个别元素的特殊性，在删除元素时替换元素上浮，导致已经遍历的位置替换为新元素，所以这样的元素均放置在一个deque中，priorityqueue遍历完成后再遍历deque，无法保证顺序

### 转换数组

- Object[] toArray()

```java
    /**
     * Returns an array containing all of the elements in this queue.
     * The elements are in no particular order.
     *
     * <p>The returned array will be "safe" in that no references to it are
     * maintained by this queue.  (In other words, this method must allocate
     * a new array).  The caller is thus free to modify the returned array.
     *
     * <p>This method acts as bridge between array-based and collection-based
     * APIs.
     *
     * @return an array containing all of the elements in this queue
     */
    public Object[] toArray() {
        return Arrays.copyOf(queue, size);
    }
```

- T[] toArray(T[] a)

```java
    /**
     * Returns an array containing all of the elements in this queue; the
     * runtime type of the returned array is that of the specified array.
     * The returned array elements are in no particular order.
     * If the queue fits适合 in the specified array, it is returned therein.
     * Otherwise, a new array is allocated with the runtime type of the
     * specified array and the size of this queue.
     *
     * <p>If the queue fits in the specified array with room to spare
     * (i.e., the array has more elements than the queue), the element in
     * the array immediately following the end of the collection is set to
     * {@code null}.
     *
     * <p>Like the {@link #toArray()} method, this method acts as bridge between
     * array-based and collection-based APIs.  Further, this method allows
     * precise control over the runtime type of the output array, and may,
     * under certain circumstances, be used to save allocation costs.
     *
     * <p>Suppose {@code x} is a queue known to contain only strings.
     * The following code can be used to dump the queue into a newly
     * allocated array of {@code String}:
     *
     *  <pre> {@code String[] y = x.toArray(new String[0]);}</pre>
     *
     * Note that {@code toArray(new Object[0])} is identical in function to
     * {@code toArray()}.
     *
     * @param a the array into which the elements of the queue are to
     *          be stored, if it is big enough; otherwise, a new array of the
     *          same runtime type is allocated for this purpose.
     * @return an array containing all of the elements in this queue
     * @throws ArrayStoreException if the runtime type of the specified array
     *         is not a supertype of the runtime type of every element in
     *         this queue
     * @throws NullPointerException if the specified array is null
     */
    @SuppressWarnings("unchecked")
    public <T> T[] toArray(T[] a) {
        final int size = this.size;
        // 如果参数数组长度小，就返回新的数组
        if (a.length < size)
            // Make a new array of a's runtime type, but my contents:
            return (T[]) Arrays.copyOf(queue, size, a.getClass());
        System.arraycopy(queue, 0, a, 0, size);
        if (a.length > size)
            a[size] = null;
        return a;
    }
```

#### 注意

- 无参方法的底层数组仍然是Object[]，无法转型
- toArray(T[] a)方法返回值应该被接收，参数数组引用可能无法被正常赋值

```java
    static void toArrayTest() {
        Queue<Integer> queue = new PriorityQueue<>();
        queue.addAll(Arrays.asList(0, 5, 3, 6, 3, 7, 4));
        Integer[] a = new Integer[queue.size()-1];
        // 指定数组长度短，重新创建一个数组后没有传给参数数组引用
        queue.toArray(a);
        // 输出：[null, null, null, null, null, null]
        System.out.println(Arrays.toString(a));
        
        // 将新数组引用赋值
        a = queue.toArray(a);
        // 输出：[0, 3, 3, 6, 5, 7, 4]
        System.out.println(Arrays.toString(a));
    }
```





参考： [2.4  Priority Queues](https://algs4.cs.princeton.edu/24pq) 