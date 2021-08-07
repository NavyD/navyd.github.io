# ArrayList

List 接口的大小可变数组的实现。实现了所有可选列表操作，并允许包括 null 在内的所有元素。

size、isEmpty、get、set、iterator 和 listIterator 操作都以固定时间运行。add 操作以分摊的固定时间 运行，也就是说，添加 n 个元素需要 O(n) 时间。其他所有操作都以线性时间运行（大体上讲）。

## 类结构

![](../../../../../assets/images/7fe7721e-5363-40c8-8041-c71e5d402292.png)

```
AbstractList (java.util)
    AbstractCollection (java.util)
        Object (java.lang)
        Collection (java.util)
            Iterable (java.lang)
    List (java.util)
        Collection (java.util)
            Iterable (java.lang)
List (java.util)
    Collection (java.util)
        Iterable (java.lang)
RandomAccess (java.util)
Cloneable (java.lang)
Serializable (java.io)
```

## 主要字段

```java
/**
 * Default initial capacity.
 */
private static final int DEFAULT_CAPACITY = 10;
/**
 * Shared empty array instance used for empty instances.
 */
// 用户显式指定list为空时使用的数组
private static final Object[] EMPTY_ELEMENTDATA = {};
/**
 * Shared empty array instance used for default sized empty instances. We
 * distinguish this from EMPTY_ELEMENTDATA to know how much to inflate when
 * first element is added.
 */
// 当使用默认无参构造器创建的空list数组，在扩容时会考虑使用默认的扩容方案DEFAULT_CAPACITY
private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};
/**
 * The array buffer into which the elements of the ArrayList are stored.
 * The capacity of the ArrayList is the length of this array buffer. Any
 * empty ArrayList with elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA
 * will be expanded to DEFAULT_CAPACITY when the first element is added.
 */
transient Object[] elementData; // non-private to simplify nested class access
/**
 * The size of the ArrayList (the number of elements it contains).
 * @serial
 */
private int size;
```

### 构造器

ArrayList所有的构造器：

![](images/arraylist_1.png)

ArrayList提供了3个构造器，除了Collection集合标准中提供无参和Collection参数的两个构造器外，额外提供int参数用于数组容量的初始化

#### 无参构造

默认无参构造器会使用一个默认空的元素数组：`DEFAULTCAPACITY_EMPTY_ELEMENTDATA`，用于区别用户显式指定(通过另外两个构造器)为空的元素数组：EMPTY_ELEMENTDATA。

```java
/**
构造一个空列表。默认的初始容量grow时为10并不是在初始时就创建，而是在需要空间时初始化
*/
public ArrayList() {
    this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}
```

与初始容量构造方式区别在于：[首次扩容](#扩容)时oldCapacity==0无参构造会默认扩容为DEFAULT_CAPACITY=10

#### Collection构造

对于参数为Collection的构造器应该少用Arrays.asList()将数组转化为ArrayList。

由于Arrays.asList().toArray()的方法不能将原数组转化为Object[]，构造器会再次将数组复制为Object[]，造成Arrays.asList().toArray()这一个额外的开销(内部实现为`arr.clone()`)，如果数组过大将造成明显的性能损失

```java
/**
构造一个使用指定 collection 并按其元素迭代的顺序排列的列表。 
*/
public ArrayList(Collection<? extends E> c) {
    // 集合c元素的object[]数组(不能确保一定为实际类型为object类型)
    elementData = c.toArray();
    if ((size = elementData.length) != 0) {
        // c.toArray might (incorrectly) not return Object[] (see 6260652)	// 如果实际类型不是Object就复制到新Object数组中
        if (elementData.getClass() != Object[].class)
            elementData = Arrays.copyOf(elementData, size, Object[].class);
    } 
    // 传入是一个空的collection
    else {
        // replace with empty array.
        this.elementData = EMPTY_ELEMENTDATA;
    }
}
```

##### Bug: JDK-6260652

###### JDK 8

在JDK8源码中关于构造器`ArrayList(Collection<? extends E> c)`源代码中`c.toArray might (incorrectly) not return Object[] (see 6260652)`的看法

```java
static void toArrayTest() {
    String[] strs = {"s", "t", "r"};
    List<String> list = Arrays.asList(strs);
    System.out.println(list.toArray());
    System.out.println(list.toArray(new Object[strs.length]));
    /*输出：
    [Ljava.lang.String;@15db9742
    [Ljava.lang.Object;@6d06d69c
    */
}
```

当使用Arrays.asList()将数组转化为List接口时，list.toArray()的行为不一致，导致直接将数组类型仍然为原数组类型String，下面是Arrays.asList()内部实现`ArrayList.toArray()`方法源码，；直接clone()，所以才保持原数组类型。

```java
@Override
public Object[] toArray() {
    return a.clone();
}
```

可能在jdk 9已修复

###### JDK 14

在jdk 14中测试上面的`toArrayTest`方法，输出已修复与`java.util.List.toArray`语义一致：

```java
jshell> toArrayTest()
[Ljava.lang.Object;@238e0d81
[Ljava.lang.Object;@31221be2
```

`java.util.Arrays.ArrayList#toArray`方法：

```java
@Override
public Object[] toArray() {
    return Arrays.copyOf(a, a.length, Object[].class);
}
```

#### 初始容量构造

创建ArrayList时应该显式指定list的容量，不应该指定容量为0

在add首次扩容时，指定容量为0的EMPTY_ELEMENTDATA的扩容为1，初始数组容量过小，造成频繁的扩容操作

```java
/**
构造一个具有指定初始容量并立即初始化分配空间的空列表。 
*/
public ArrayList(int initialCapacity) {
    if (initialCapacity > 0) {
        this.elementData = new Object[initialCapacity];
    } else if (initialCapacity == 0) {
        this.elementData = EMPTY_ELEMENTDATA;
    } else {
        throw new IllegalArgumentException("Illegal Capacity: "+
                                            initialCapacity);
    }
}
```

### 扩容

通过无参构造器设置默认扩容为DEFAULT_CAPACITY=10，其余构造器默认扩容为0，对于默认构造的list实例，每次扩容都需要将指定容量与默认容量比较，选择较大的扩容

如果指定的扩容容量小于当前数组长度，将不会发生实质的扩容操作

每次实际扩容的容量至少在1.5倍旧容量或更大的指定容量，不会造成频繁的扩容操作

```java
/**
     * Increases the capacity of this <tt>ArrayList</tt> instance, if
     * necessary, to ensure that it can hold at least the number of elements
     * specified by the minimum capacity argument.
     *
     * @param   minCapacity   the desired minimum capacity
     */
    // 如果指定的容量比默认的方案大，就设置为指定容量扩容。
    public void ensureCapacity(int minCapacity) {
        // 默认空的list实例最小扩容为10，否则就为0。elementData设置为非DEFAULTCAPACITY_EMPTY_ELEMENTDATA表示用户指定了容量或collection构造arrayList
        int minExpand = (elementData != DEFAULTCAPACITY_EMPTY_ELEMENTDATA)
            // any size if not default element table
            ? 0
            // larger than default for default empty table. It's already
            // supposed to be at default size.
            : DEFAULT_CAPACITY;

        if (minCapacity > minExpand) {
            ensureExplicitCapacity(minCapacity);
        }
    }
```

扩容的私有方法实现：

```java
    // 在指定容量和默认容量间选择更大的扩容容量
    private void ensureCapacityInternal(int minCapacity) {
        // 如果是默认大小的list实例，最小容量应该比默认容量10要大，否则使用默认容量
        if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
            minCapacity = Math.max(DEFAULT_CAPACITY, minCapacity);
        }

        ensureExplicitCapacity(minCapacity);
    }

    /**
     * 如果指定的容量大于数组长度elementData.length就调用grow()扩大数组
     * @param minCapacity
     */
    private void ensureExplicitCapacity(int minCapacity) {
        modCount++;

        // overflow-conscious code
        // 如果期望容量大于当前数组容量就扩大数组
        if (minCapacity - elementData.length > 0)
            grow(minCapacity);
    }

    /**
     * Increases the capacity to ensure that it can hold at least the
     * number of elements specified by the minimum capacity argument.
     *
     * @param minCapacity the desired minimum capacity
     */
    // 扩大数组容量为1.5倍旧容量或更大的指定容量
    private void grow(int minCapacity) {
        // overflow-conscious code
        int oldCapacity = elementData.length;
        // 新容量为旧容量的1.5倍
        int newCapacity = oldCapacity + (oldCapacity >> 1);
        // 如果指定容量大于1.5倍旧容量就取指定容量
        if (newCapacity - minCapacity < 0)
            newCapacity = minCapacity;
        // 如果新容量超过数组最大容量
        if (newCapacity - MAX_ARRAY_SIZE > 0)
            newCapacity = hugeCapacity(minCapacity);
        // minCapacity is usually close to size, so this is a win:
        elementData = Arrays.copyOf(elementData, newCapacity);
    }
    // 如果指定容量超过2^31就抛出异常，否则将容量设置为Integer.MAX_VALUE
    private static int hugeCapacity(int minCapacity) {
        if (minCapacity < 0) // overflow
            throw new OutOfMemoryError();
        return (minCapacity > MAX_ARRAY_SIZE) ?
            Integer.MAX_VALUE :
            MAX_ARRAY_SIZE;
    }
```

## 查询

```java
    public int size() {
        return size;
    }
    public boolean isEmpty() {
        return size == 0;
    }
	// 具体indexOf()看后面
    public boolean contains(Object o) {
        return indexOf(o) >= 0;
    } 
```

## 搜索

- int indexOf(Object o)

```java
    /**
     * Returns the index of the first occurrence of the specified element
     * in this list, or -1 if this list does not contain the element.
     * More formally, returns the lowest index <tt>i</tt> such that
     * <tt>(o==null&nbsp;?&nbsp;get(i)==null&nbsp;:&nbsp;o.equals(get(i)))</tt>,
     * or -1 if there is no such index.
     */
    // 覆盖AbstractList的实现，通过数组下标随机访问加快速度，而不是通过迭代器访问
    public int indexOf(Object o) {
        // 如果指定参数为null,就在数组中搜索为null的元素
        if (o == null) {
            for (int i = 0; i < size; i++)
                if (elementData[i]==null)
                    return i;
        } 
        // 否则就在数组中寻找与指定参数相等的元素
        else {
            for (int i = 0; i < size; i++)
                if (o.equals(elementData[i]))
                    return i;
        }
        return -1;
    }
```

- int lastIndexOf(Object o)

```java
    /**
     * Returns the index of the last occurrence of the specified element
     * in this list, or -1 if this list does not contain the element.
     * More formally, returns the highest index <tt>i</tt> such that
     * <tt>(o==null&nbsp;?&nbsp;get(i)==null&nbsp;:&nbsp;o.equals(get(i)))</tt>,
     * or -1 if there is no such index.
     */
    public int lastIndexOf(Object o) {
        if (o == null) {
            // 从数组最后往前遍历
            for (int i = size-1; i >= 0; i--)
                if (elementData[i]==null)
                    return i;
        } else {
            for (int i = size-1; i >= 0; i--)
                if (o.equals(elementData[i]))
                    return i;
        }
        return -1;
    }
```



## 转换

- Object[] toArray()

```java
    /**
     * Returns an array containing all of the elements in this list
     * in proper sequence (from first to last element).
     */
	// 复制ArrayList底层数组为一个Object[]
    public Object[] toArray() {
        return Arrays.copyOf(elementData, size);
    }
```



- T[] toArray(T[] a)

```java
    /**
     * Returns an array containing all of the elements in this list in proper
     * sequence (from first to last element); the runtime type of the returned
     * array is that of the specified array.  If the list fits in the
     * specified array, it is returned therein.  Otherwise, a new array is
     * allocated with the runtime type of the specified array and the size of
     * this list.
     *
     * <p>If the list fits in the specified array with room to spare
     * (i.e., the array has more elements than the list), the element in
     * the array immediately following the end of the collection is set to
     * <tt>null</tt>.  (This is useful in determining the length of the
     * list <i>only</i> if the caller knows that the list does not contain
     * any null elements.)
     */
	// 将集合转换为指定数组类型。如果指定数组长度小于集合大小，就填充到新数组，如果大于就在数组的集合元素最后位置（collection.size()）置为null
    @SuppressWarnings("unchecked")
    public <T> T[] toArray(T[] a) {
        if (a.length < size)
            // Make a new array of a's runtime type, but my contents:
            return (T[]) Arrays.copyOf(elementData, size, a.getClass());
        System.arraycopy(elementData, 0, a, 0, size);
        // 如果指定的数组长度大于list的数组，只将指定数组的list.size()处置为null
        if (a.length > size)
            a[size] = null;
        return a;
    }
```

### 注意

- T[] toArray(T[] a)的参数数组长度应该设置为a.length = collection.size()

如果设置length过小，Arrays.copyOf会通过反射重新创建指定类型的空数组并将元素复制过去，会造成反射和创建对象的开销。

- T[] toArray(T[] a)对于过大的指定数组长度时会将`a[list.size()]`位置置为null，但其后续元素仍然存在，使用数组时需要注意

## 添加

- boolean add(E e)

```java
    /**
     * Appends the specified element to the end of this list.
     *
     * @param e element to be appended to this list
     * @return <tt>true</tt> (as specified by {@link Collection#add})
     */
    public boolean add(E e) {
        // 只有当size+1 > 数组.length时才会执行扩容，每次扩容至少在1.5倍旧容量之上
        ensureCapacityInternal(size + 1);  // Increments modCount!!
        elementData[size++] = e;
        return true;
    } `
```

- void add(int index, E element)

```java
    /**
     * Inserts the specified element at the specified position in this
     * list. Shifts the element currently at that position (if any) and
     * any subsequent elements to the right (adds one to their indices).
     *
     * @param index index at which the specified element is to be inserted
     * @param element element to be inserted
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public void add(int index, E element) {
        // 检查index下界和上界，检查下界是防止System.arraycopy抛出异常IndexOutOfBoundsException
        rangeCheckForAdd(index);

        ensureCapacityInternal(size + 1);  // Increments modCount!!
        System.arraycopy(elementData, index, elementData, index + 1,
                         size - index);
        elementData[index] = element;
        size++;
    }
```

- boolean addAll(Collection<? extends E> c)

```java
    /**
     * Appends all of the elements in the specified collection to the end of
     * this list, in the order that they are returned by the
     * specified collection's Iterator.  The behavior of this operation is
     * undefined if the specified collection is modified while the operation
     * is in progress.  (This implies that the behavior of this call is
     * undefined if the specified collection is this list, and this
     * list is nonempty.)
     *
     * @param c collection containing elements to be added to this list
     * @return <tt>true</tt> if this list changed as a result of the call
     * @throws NullPointerException if the specified collection is null
     */
    public boolean addAll(Collection<? extends E> c) {
        // 集合转为Object[] 即使底层数组不是Object也没关系，会将数组元素复制到list的Object[]
        Object[] a = c.toArray();
        int numNew = a.length;
        ensureCapacityInternal(size + numNew);  // Increments modCount
        System.arraycopy(a, 0, elementData, size, numNew);
        size += numNew;
        return numNew != 0;
    }
```

- boolean addAll(int index, Collection<? extends E> c)

```java
    /**
     * Inserts all of the elements in the specified collection into this
     * list, starting at the specified position.  Shifts the element
     * currently at that position (if any) and any subsequent elements to
     * the right (increases their indices).  The new elements will appear
     * in the list in the order that they are returned by the
     * specified collection's iterator.
     *
     * @param index index at which to insert the first element from the
     *              specified collection
     * @param c collection containing elements to be added to this list
     * @return <tt>true</tt> if this list changed as a result of the call
     * @throws IndexOutOfBoundsException {@inheritDoc}
     * @throws NullPointerException if the specified collection is null
     */
    public boolean addAll(int index, Collection<? extends E> c) {
        rangeCheckForAdd(index);

        Object[] a = c.toArray();
        int numNew = a.length;
        // 扩大数组
        ensureCapacityInternal(size + numNew);  // Increments modCount

        int numMoved = size - index;
        // 如果插入位置index不在末尾
        if (numMoved > 0)
            // 移动index及以后的元素，将index--index+numNew-1的位置空出来
            System.arraycopy(elementData, index, elementData, index + numNew,
                             numMoved);
        // 将集合数组元素插入到指定位置index
        System.arraycopy(a, 0, elementData, index, numNew);
        size += numNew;
        return numNew != 0;
    }
```

### 注意

- 添加单个元素时，并不会在每次添加时扩容，需要满足size==elementData.length时才会扩容，容量为1.5倍旧容量或更高

add()源代码中使用ensureCapacityInternal(size + 1)，需要满足size+1>elementData.length才会准备扩容。需要注意默认构造的arraylist实例首次扩容为10，之后才是1.5倍或更高

- 插入指定位置需要额外的移动之后的元素造成很大的开销


## 删除

- void clear()

```java
    /**
     * Removes all of the elements from this list.  The list will
     * be empty after this call returns.
     */
    // 此实现将数组所有数组元素置为null
    public void clear() {
        modCount++;

        // clear to let GC do its work
        for (int i = 0; i < size; i++)
            elementData[i] = null;

        size = 0;
    }
```

- E remove(int index)

```java
    /**
     * Removes the element at the specified position in this list.
     * Shifts any subsequent elements to the left (subtracts one from their
     * indices).
     *
     * @param index the index of the element to be removed
     * @return the element that was removed from the list
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public E remove(int index) {
        // 检查index的上界
        rangeCheck(index);

        modCount++;
        E oldValue = elementData(index);

        int numMoved = size - index - 1;
        // 如果指定索引不是最后一个元素(size-1)，就左移index后的元素一位到index
        if (numMoved > 0)
            System.arraycopy(elementData, index+1, elementData, index,
                             numMoved);
        // 将最后一个元素置为null，删除
        elementData[--size] = null; // clear to let GC do its work

        return oldValue;
    }
```

- boolean remove(Object o)

```java
    /**
     * Removes the first occurrence of the specified element from this list,
     * if it is present.  If the list does not contain the element, it is
     * unchanged.  More formally, removes the element with the lowest index
     * <tt>i</tt> such that
     * <tt>(o==null&nbsp;?&nbsp;get(i)==null&nbsp;:&nbsp;o.equals(get(i)))</tt>
     * (if such an element exists).  Returns <tt>true</tt> if this list
     * contained the specified element (or equivalently, if this list
     * changed as a result of the call).
     *
     * @param o element to be removed from this list, if present
     * @return <tt>true</tt> if this list contained the specified element
     */
    public boolean remove(Object o) {
        if (o == null) {
            for (int index = 0; index < size; index++)
                if (elementData[index] == null) {
                 // 通过左移来删除元素，仅减少了范围检查和返回值获取
                    fastRemove(index);
                    return true;
                }
        } else {
            for (int index = 0; index < size; index++)
                if (o.equals(elementData[index])) {
                    // 通过左移来删除元素，仅减少了范围检查和返回值获取
                    fastRemove(index);
                    return true;
                }
        }
        return false;
    }

    /*
     * Private remove method that skips bounds checking and does not
     * return the value removed.
     */
    private void fastRemove(int index) {
        modCount++;
        int numMoved = size - index - 1;
        // 如果index不是最后一个元素索引就将index后的元素向左移动一位
        if (numMoved > 0)
            System.arraycopy(elementData, index+1, elementData, index,
                             numMoved);
        elementData[--size] = null; // clear to let GC do its work
    }
```

- boolean removeAll(Collection<?> c)

```java
    /**
     * Removes from this list all of its elements that are contained in the
     * specified collection.
     */
    public boolean removeAll(Collection<?> c) {
        Objects.requireNonNull(c);
        return batchRemove(c, false);
    }
```

- boolean retainAll(Collection<?> c)

```java
    /**
     * Retains only the elements in this list that are contained in the
     * specified collection.  In other words, removes from this list all
     * of its elements that are not contained in the specified collection.
     */
    public boolean retainAll(Collection<?> c) {
        Objects.requireNonNull(c);
        return batchRemove(c, true);
    }
```

私有方法：

```java
    /**
     * 如果complement==false，删除list中包含在collection的元素
     * 如果complement==true,删除list中不包含在指定collection中的元素
     * @param c
     * @param complement
     * @return
     */
    private boolean batchRemove(Collection<?> c, boolean complement) {
        final Object[] elementData = this.elementData;
        // r用于在原数组中遍历，w用于在保留到原数组的下标
        int r = 0, w = 0;
        boolean modified = false;
        try {
            // 遍历此list数组元素
            for (; r < size; r++)
                // 如果指定collection的元素存在于此list中   根据complement策略选择是否保留到数组中
                if (c.contains(elementData[r]) == complement)
                    // 在原数组中从0开始覆盖为新元素
                    elementData[w++] = elementData[r];
        } finally {
            // Preserve behavioral compatibility with AbstractCollection,
            // even if c.contains() throws.
            // 由于collection可能会跑出异常，try-finally保证在异常抛出后仍然可以正常删除
            // 如果抛出异常，在该元素后的所有元素将会被正常保留，不管是否在存在于collection中
            if (r != size) {
                System.arraycopy(elementData, r,
                                 elementData, w,
                                 size - r);
                w += size - r;
            }
            // 将数组保留元素之后的未覆盖的原数组元素置为null
            if (w != size) {
                // clear to let GC do its work
                for (int i = w; i < size; i++)
                    elementData[i] = null;
                // 数组元素改变的次数应该反应到修改计数器
                modCount += size - w;
                size = w;
                modified = true;
            }
        }
        return modified;
    }
```

- boolean removeIf(Predicate<? super E> filter)

```java
    // 移除在list中所有符合条件的元素
    // 通过BitSet保存符合条件的索引，再元素复制循环中跳过bitSet为true的索引元素
    @Override
    public boolean removeIf(Predicate<? super E> filter) {
        Objects.requireNonNull(filter);
        // figure out which elements are to be removed
        // any exception thrown from the filter predicate at this stage
        // will leave the collection unmodified
        int removeCount = 0;
        // 创建一个从0--size-1索引的bitSet，用于表示在原数组中需要删除的索引位置
        final BitSet removeSet = new BitSet(size);
        final int expectedModCount = modCount;
        final int size = this.size;
        // 遍历list的数组找出符合条件要删除元素的索引位置
        for (int i=0; modCount == expectedModCount && i < size; i++) {
            @SuppressWarnings("unchecked")
            final E element = (E) elementData[i];
            // 如果数组中存在元素符合条件filter
            if (filter.test(element)) {
                // 设置bitSet对应索引位置为true
                removeSet.set(i);
                removeCount++;
            }
        }
        if (modCount != expectedModCount) {
            throw new ConcurrentModificationException();
        }

        // shift surviving elements left over the spaces left by removed elements
        // 如果存在符合条件的元素
        final boolean anyToRemove = removeCount > 0;
        if (anyToRemove) {
            // 新的元素个数
            final int newSize = size - removeCount;
            // 遍历原数组并将保留的元素移动到数组最左边
            for (int i=0, j=0; (i < size) && (j < newSize); i++, j++) {
                // 返回从当前索引i开始bit为false的索引  如：{0:false, 1:true, 2:false]
                // nextClearBit(0)返回0，nextClearBit(1)返回2
                // 跳过符合条件的即被删除的元素索引
                i = removeSet.nextClearBit(i);
                elementData[j] = elementData[i];
            }
            // 将未覆盖的旧元素置为null
            for (int k=newSize; k < size; k++) {
                elementData[k] = null;  // Let gc do its work
            }
            this.size = newSize;
            if (modCount != expectedModCount) {
                throw new ConcurrentModificationException();
            }
            modCount++;
        }

        return anyToRemove;
    }
```

### 注意

- 所有删除操作最后都是将数组元素左移覆盖原数组元素，然后将未覆盖掉的位置置为null

- void clear()不是简单的将elementData替换为新数组，而是将所有元素置为null来达到清空效果

- 在removeAll()和retainAll()允许collection与list元素类型存在异常时仍然能够正确的删除异常前的元素，异常元素即后面的元素会仍然存在于list中

这两个方法的私有实现batchRemove(Collection<?> c, boolean complement)的collection.contains()在与list的数组比较时，如果contains()抛出异常不会中断该方法，只是异常后的元素默认保留在list中，即使存在与collection中也不会删除list对应的元素

- Java8新增的方法removeIf()的实现与batchRemove()大同小异，都是在原数组中找到指定的元素下标，然后移动整个数组元素。前者找到所有指定元素后在移动，后者是边找边移动

removeIf的实现使用BitSet记录满足条件的元素下标，并不会处理异常，如果Predicate.test()抛出异常会停止方法运行。另外在modCount用for验证更加频繁。支持函数式编程：

```java
    static void removeIfTest() {
        List<String> list = new ArrayList<>(5);
        list.add("s");
        list.add("st");
        list.add("str");
      	// 不能使用==比较，虽然指向同一个常量池对象
//        list.removeIf(s-> s == "st");
		list.removeIf(s-> s.equals("st"));
      	// 输出：[s, str]
        System.out.println(list);
    }
```

## 迭代

- void forEach(Consumer<? super E> action)

```java
    // 对Iterable的每个元素执行给定的操作。按照迭代器的顺序迭代元素
    @Override
    public void forEach(Consumer<? super E> action) {
        Objects.requireNonNull(action);
        final int expectedModCount = modCount;
        // 由于类型擦除的机制，实际并没有转型为E，仍然为Object[]
        @SuppressWarnings("unchecked")
        final E[] elementData = (E[]) this.elementData;
        final int size = this.size;
        // 遍历元素数组并检查结构修改的可能
        for (int i=0; modCount == expectedModCount && i < size; i++) {
            action.accept(elementData[i]);
        } 
        if (modCount != expectedModCount) {
            throw new ConcurrentModificationException();
        }
    }
```

- Iterator<E> iterator() 

```java
    public Iterator<E> iterator() {
        return new Itr();
    }
```

- ListIterator<E> listIterator()

```java
    public ListIterator<E> listIterator() {
        return new ListItr(0);
    }

    public ListIterator<E> listIterator(int index) {
        if (index < 0 || index > size)
            throw new IndexOutOfBoundsException("Index: "+index);
        return new ListItr(index);
    }
```

### 迭代器实现

```java
    /**
     * An optimized version of AbstractList.Itr
     */
    private class Itr implements Iterator<E> {
        int cursor;       // index of next element to return
        int lastRet = -1; // index of last element returned; -1 if no such
        int expectedModCount = modCount;

        public boolean hasNext() {
            return cursor != size;
        }

        @SuppressWarnings("unchecked")
        public E next() {
            checkForComodification();
            int i = cursor;
            if (i >= size)
                throw new NoSuchElementException();
            Object[] elementData = ArrayList.this.elementData;
            if (i >= elementData.length)
                throw new ConcurrentModificationException();
            cursor = i + 1;
            return (E) elementData[lastRet = i];
        }

        public void remove() {
            if (lastRet < 0)
                throw new IllegalStateException();
            checkForComodification();

            try {
                // 通过上一次调用的元素下标删除对应元素
                ArrayList.this.remove(lastRet);
                // 将光标设置为删除元素的位置。
                cursor = lastRet;
                /**
                 *  next调用后cursor+1=lastRet，previous调用后cursor=lastRet
                 *  next后删除需要光标移后一位即cursor=lastRet，previous后删除不需要移动光标
                 *  但是，cursor=lastRet也没有错误，同时减少的每次的比较操作，算是优化
                 */
//                if (lastRet < cursor)
//                    cursor--;
                lastRet = -1;
                expectedModCount = modCount;
            } catch (IndexOutOfBoundsException ex) {
                throw new ConcurrentModificationException();
            }
        }
        // 用于在当前迭代器位置下对剩下的所有元素执行指定的动作
        @Override
        @SuppressWarnings("unchecked")
        public void forEachRemaining(Consumer<? super E> consumer) {
            Objects.requireNonNull(consumer);
            final int size = ArrayList.this.size;
            int i = cursor;
            if (i >= size) {
                return;
            }
            final Object[] elementData = ArrayList.this.elementData;
            if (i >= elementData.length) {
                throw new ConcurrentModificationException();
            }
            // 循环遍历和检查线程修改
            while (i != size && modCount == expectedModCount) {
                consumer.accept((E) elementData[i++]);
            }
            // update once at end of iteration to reduce heap write traffic
            cursor = i;
            lastRet = i - 1;
            checkForComodification();
        }

        final void checkForComodification() {
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
        }
    }

    /**
     * An optimized version of AbstractList.ListItr
     */
    private class ListItr extends Itr implements ListIterator<E> {
        ListItr(int index) {
            super();
            cursor = index;
        }

        public boolean hasPrevious() {
            return cursor != 0;
        }

        public int nextIndex() {
            return cursor;
        }

        public int previousIndex() {
            return cursor - 1;
        }

        @SuppressWarnings("unchecked")
        public E previous() {
            checkForComodification();
            int i = cursor - 1;
            if (i < 0)
                throw new NoSuchElementException();
            Object[] elementData = ArrayList.this.elementData;
            if (i >= elementData.length)
                throw new ConcurrentModificationException();
            cursor = i;
            return (E) elementData[lastRet = i];
        }

        public void set(E e) {
            if (lastRet < 0)
                throw new IllegalStateException();
            checkForComodification();

            try {
                ArrayList.this.set(lastRet, e);
            } catch (IndexOutOfBoundsException ex) {
                throw new ConcurrentModificationException();
            }
        }

        public void add(E e) {
            checkForComodification();

            try {
                int i = cursor;
                ArrayList.this.add(i, e);
                cursor = i + 1;
                lastRet = -1;
                expectedModCount = modCount;
            } catch (IndexOutOfBoundsException ex) {
                throw new ConcurrentModificationException();
            }
        }
    }
```

### 注意

- ArrayList的迭代器与AbstractList的实现并没有过大的区别

相比之下，前者的next()和previous()增加了两层检查：对下标i过界抛出nosuchelement和concurrentmodifi异常，而对remove()减少了一次比较

- ArrayList迭代器与使用for相比主要性能差别在与迭代器需要多重检查和方法调用， 实际都是通过下标访数组元素
- 与直接的for相比foreach()更加方便和安全，后者提供快速失败的功能
- 对于在foreach()中的数组转型的疑问，实际上Object[]底层数组是不能被转型的，但是无边界范型仍然为object，因此允许转型

```java
    //  协变类型不能转型Object
	@SuppressWarnings("unchecked")
    static <T extends Number> void arrayConvertTest(T t) {
//        Object[] objs = {"t", "tt"};
        Object[] objs = {1, 2};
        System.out.println(objs.getClass().getName());
      	// 异常：java.lang.ClassCastException: [Ljava.lang.Object; cannot be cast to [Ljava.lang.Number;[Ljava.lang.Object;
        T[] ts = (T[]) objs;
        System.out.println(ts.getClass().getName());
    }
```

## 替换

- E set(int index, E element)

```java
    public E set(int index, E element) {
        rangeCheck(index);

        E oldValue = elementData(index);
        elementData[index] = element;
        return oldValue;
    }
```

- void replaceAll(UnaryOperator<E> operator)

```java
    // 将此列表中的每个元素替换为指定操作中应用的结果。
    @Override
    @SuppressWarnings("unchecked")
    public void replaceAll(UnaryOperator<E> operator) {
        Objects.requireNonNull(operator);
        final int expectedModCount = modCount;
        final int size = this.size;
        // 遍历所有元素并检查线程修改
        for (int i=0; modCount == expectedModCount && i < size; i++) {
            elementData[i] = operator.apply((E) elementData[i]);
        }
        if (modCount != expectedModCount) {
            throw new ConcurrentModificationException();
        }
        modCount++;
    }
```

### 注意

- 对于线程修改`modCount`的检查replaceAll的实现与removeIf均一致，都是在for中每次循环检查一次
- 关于replaceAll(UnaryOperator<E> operator)的使用

```java
    static void replaceTest() {
        List<String> list = new ArrayList<>();
        list.addAll(Arrays.asList("a", "ab", "abc"));
        /**
         * UnaryOperator用于指定参数和返回同类型的结果
         * UnaryOperator<T> extends Function<T, T>:T apply(T t)
         */
        list.replaceAll(s -> {
          	// 输出list每一个元素
            System.out.println(s);
            return s.toUpperCase();
        });
        System.out.println(list);
    }
```

`UnaryOperator<E>`表示单操作数返回同类型的结果的函数操作，List包含的类型就只允许replaceAll返回同样的类型

## SubList

- List<E> subList(int fromIndex, int toIndex)

```java
    public List<E> subList(int fromIndex, int toIndex) {
        subListRangeCheck(fromIndex, toIndex, size);
        return new SubList(this, 0, fromIndex, toIndex);
    }
```

私有实现：

```java
    static void subListRangeCheck(int fromIndex, int toIndex, int size) {
        if (fromIndex < 0)
            throw new IndexOutOfBoundsException("fromIndex = " + fromIndex);
        if (toIndex > size)
            throw new IndexOutOfBoundsException("toIndex = " + toIndex);
        if (fromIndex > toIndex)
            throw new IllegalArgumentException("fromIndex(" + fromIndex +
                                               ") > toIndex(" + toIndex + ")");
    }
	/**
   		与AbstractList的实现类似，均为在偏移量offset上调用原list对应方法，对于
   		subList.listIterator()的实现也只是在AbstratList的基础上将原ArrayList的
   		listIterator对象的调用转而自己实现，但是该实现绝大部分ArrayList．ListIterator相同
    */
    private class SubList extends AbstractList<E> implements RandomAccess {
```

### 注意

- `SubList extends AbstractList<E> implements RandomAccess`不是ArrayList类型，不能把SubList转化为ArrayList，会报异常：`java.lang.ClassCastException: src.java.util.ArrayList$SubList cannot be cast to src.java.util.ArrayList`

```java
    static void subListTest() {
        List<String> list = new ArrayList<>(3);
        list.addAll(Arrays.asList("a", "ab", "abc"));
        List<String> subList = list.subList(0, 2);
      	// class java.util.AbstractList
        System.out.println(subList.getClass().getSuperclass());
      	// java.util.ArrayList$SubList
        System.out.println(subList.getClass().getName());
        subList.forEach(s -> System.out.println(s));
      	// 异常
//        ArrayList<String> aList = (ArrayList<String>)subList;
    }
```

- 具体实现请参考AbstractList和源码，两者大同小异

## 参考

- [https://bugs.java.com/bugdatabase/view_bug.do?bug_id=6260652](https://bugs.java.com/bugdatabase/view_bug.do?bug_id=6260652 "JDK-6260652 : (coll) Arrays.asList(x).toArray().getClass() should be Object[].[class")

