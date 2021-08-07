# AbstractCollection #

此类提供 Collection 接口的骨干实现，以最大限度地减少了实现此接口所需的工作。

```java
public abstract class AbstractCollection<E> implements Collection<E>
```

## 抽象方法 ##

```java
/**
返回该集合中包含的元素的迭代器。
*/
public abstract Iterator<E> iterator();

public abstract int size();
```

## 不支持方法 ##

```java
    public boolean add(E e) {
        throw new UnsupportedOperationException();
    }
```

## 实现方法 ##

### 添加 ###

1. addAll(Collection<? extends E> c)

```java
    /**
    此实现在指定的 collection 上进行迭代，并依次将迭代器返回的每个对象添加到此 collection 中。 
    注意：如果指定集合c存在未添加成功的元素将返回false
    */
    public boolean addAll(Collection<? extends E> c) {
        boolean modified = false;
        for (E e : c)
            if (add(e))
                modified = true;
        return modified;
    }
```
### 删除 ###

1. remove(Object o)

```java
    /**
    此实现在该 collection 上进行迭代，查找指定的元素。
    如果找到该元素，那么它会使用迭代器的 remove 方法从该 collection 中移除该元素。
    注意：如果此 collection 的 iterator.remove()未实现，并且此 collection 包含指定的对象，那么此实现将抛出 UnsupportedOperationException。 
    */
    public boolean remove(Object o) {
        Iterator<E> it = iterator();
        // 如果指定元素为null就遍历寻找null元素并调用iterator.remove()删除
        if (o==null) {
            while (it.hasNext()) {
                if (it.next()==null) {
                    it.remove();
                    return true;
                }
            }
        } 
        // 如果迭代器中存在指定元素调用iterator.remove()删除
        else {
            while (it.hasNext()) {
                if (o.equals(it.next())) {
                    it.remove();
                    return true;
                }
            }
        }
        return false;
    }
```
2. removeAll(Collection<?> c)

```java
    /**
    此实现在此 collection 上进行迭代，依次检查该迭代器返回的每个元素，以查看其是否包含在指定的 collection 中。
    如果是，则使用迭代器的 remove 方法将其从此 collection 中移除。 
    */
    public boolean removeAll(Collection<?> c) {
        Objects.requireNonNull(c);
        boolean modified = false;
        Iterator<?> it = iterator();
        while (it.hasNext()) {
            if (c.contains(it.next())) {
                it.remove();
                modified = true;
            }
        }
        return modified;
    }
```
3. retainAll(Collection<?> c)

该方法仅仅是将removeAll中改为`if (!c.contains(it.next()))`

4. clear() 

```java
    /**
    此实现在此 collection 上进行迭代，并使用 Iterator.remove 操作移除每个元素。
    为了提高效率，多数实现可能会选择重写此方法。 
    */
    public void clear() {
        Iterator<E> it = iterator();
        while (it.hasNext()) {
            it.next();
            it.remove();
        }
    }
```
### 查询 ###

1. isEmpty()

```java
    public boolean isEmpty() {
        return size() == 0;
    }

```

2. contains(Object o)

```java
    /**
    如果此 collection 包含指定的元素，则返回 true。
    在 collection 中的元素上进行迭代，并依次检查每个元素以确定其是否与指定的元素相等。
    */
    public boolean contains(Object o) {
        Iterator<E> it = iterator();
        // 如果指定元素为null就遍历寻找集合中的null元素
        if (o==null) {
            while (it.hasNext())
                if (it.next()==null)
                    return true;
        } 
        // 如果指定元素不为null就equals()
        else {
            while (it.hasNext())
                if (o.equals(it.next()))
                    return true;
        }
        return false;
    }
```
3. containsAll(Collection<?> c)

```java
    public boolean containsAll(Collection<?> c) {
        for (Object e : c)
            if (!contains(e))
                return false;
        return true;
    }
```

### 转换 ###

- toArray()

```java
    /**
    返回包含此 collection 中所有元素的数组。 使用迭代器实现数组的转换。
    即使迭代器返回不同的元素数，也会返回正确的结果。
    */
    public Object[] toArray() {
        // Estimate size of array; be prepared to see more or fewer elements
    	// 由size()预计数组的长度， 如果在该方法期间collection的size发生变化将不会导致数组元素丢失
        Object[] r = new Object[size()];
        Iterator<E> it = iterator();
        for (int i = 0; i < r.length; i++) {
        	// 如果数组元素比size预计的要少，就复制到一个充满的新数组
            if (! it.hasNext()) // fewer elements than expected
                return Arrays.copyOf(r, i);
            r[i] = it.next();
        }
        // 如果数组元素比size预计的要多，就添加更多元素到数组，否则直接返回当前完整的数组
        return it.hasNext() ? finishToArray(r, it) : r;
    }

    /**
    在迭代器iterator返回更多元素(比size()预计的多)时重新分配并从iterator中填充元素到新数组
    */
    @SuppressWarnings("unchecked")
    private static <T> T[] finishToArray(T[] r, Iterator<?> it) {
        int i = r.length;
        // 在原有iterator基础上进行迭代，不需要从头开始
        while (it.hasNext()) {
            int cap = r.length;
            // 如果数组已满就复制到newCap的新数组
            if (i == cap) {
                int newCap = cap + (cap >> 1) + 1;
                // overflow-conscious code
                if (newCap - MAX_ARRAY_SIZE > 0)
                    newCap = hugeCapacity(cap + 1);
                // 复制数组
                r = Arrays.copyOf(r, newCap);
            }

            r[i++] = (T)it.next();
        }
        // trim if overallocated
        // 如果数组容量过大就复制为更小的新数组
        return (i == r.length) ? r : Arrays.copyOf(r, i);
    }

    private static int hugeCapacity(int minCapacity) {
        if (minCapacity < 0) // overflow
            throw new OutOfMemoryError
                ("Required array size too large");
        return (minCapacity > MAX_ARRAY_SIZE) ?
            Integer.MAX_VALUE :
            MAX_ARRAY_SIZE;
    }
```
- toArray(T[] a)

```java 
    /**
    返回包含此 collection 中所有元素的指定类型的数组。如果指定的数组能容纳该 collection，则返回包含此 collection 元素的数组。
    否则，将分配一个具有指定数组的运行时类型和此 collection 大小的新数组。 
    */
    public <T> T[] toArray(T[] a) {
        // Estimate size of array; be prepared to see more or fewer elements
        int size = size();
        // 如果指定的数组a的长度比size()预计的更小，就创建一个size大小的新数组
        T[] r = a.length >= size ? a :
                  (T[])java.lang.reflect.Array
                  .newInstance(a.getClass().getComponentType(), size);
        Iterator<E> it = iterator();

        for (int i = 0; i < r.length; i++) {
        	// 数组长度比size()预计的更小时
            if (! it.hasNext()) { // fewer elements than expected
            	// 正常情况指定数组a长度大于size()，将当前数组下标置为null
                if (a == r) {
                    r[i] = null; // null-terminate
                } 
                // 异常情况可能同时remove()后导致元素减少时指定数组a长度仍然小于当前下标，直接复制到新数组
                else if (a.length < i) {
                    return Arrays.copyOf(r, i);
                } 
                // 元素减少时指定数组a长度不小于当前下标，此时将元素复制到指定数组a中
                else {
                    System.arraycopy(r, 0, a, 0, i);
                    // 指定数组长度更多
                    if (a.length > i) {
                        a[i] = null;
                    }
                }
                return a;
            }
            r[i] = (T)it.next();
        }
        // more elements than expected
        // 如果数组元素比size预计的要多，就添加更多元素到数组，否则直接返回当前完整的数组
        return it.hasNext() ? finishToArray(r, it) : r;
    }
```

注意： 

- 使用集合转数组的方法，必须使用集合的toArray(T[] array)，传入的是类型完全一样的数组，大小就是list.size()。

由于collection.toArray(T[] array)使用size()方法预计集合元素的大小，如果传入的数组过小，就会使用反射创建一个同类型的size()大小的数组。所以直接使用list.size()会减少反射的使用。如：

```java
List<String> list = new ArrayList<String>(2);
list.add("guan");
list.add("bao");
String[] array = new String[list.size()];
array = list.toArray(array);
```

另外，如果在toArray()执行期间改变集合元素数量，会造成额外的数组复制过程，不保证线程安全。一般的集合实现都有快速失败功能，但是不一定发生，不能依赖这一功能，**即不应该在迭代的时候操作集合**

参考：阿里巴巴开发手册(纪念版)

- 使用Collection.toArray()无参方法存在问题，此方法返回值只能是Object[]类，若强转其它类型数组将出现ClassCastException错误。注意Arrays.asList().toArray()无参方法存在bug，返回的数组仍然为原数组类型


```java
    static void toArrayTest() {
        List<String> aList = new ArrayList<>(3);
        aList.add("s");
        aList.add("st");
        aList.add("str");
      	// 底层数组就是Object[]
        Object[] objs = aList.toArray();
// 强转Object数组导致异常：java.lang.ClassCastException: [Ljava.lang.Object; cannot be cast to [Ljava.lang.String;
        String[] strs = (String[])objs;
    }
```



由于Collection.toArray()底层实现为`Object[] r = new Object[size()];`，是将集合元素放入Object[]中，而不是将集合元素放入指定类型的数组中(Collection.toArray(T[] a)提供该功能)。如果直接强制转换Object数组将抛出异常。原因就是数组允许向上转型但只允许实际类型赋值

```java
    static void test() {
        // 底层数组实例为String类型
        String[] strs = {"s", "st", "str"};
        // 向上转型为Object父类型
        Object[] objs = strs;
        // 尝试使用父类型Object赋值  失败  抛出异常java.lang.ArrayStoreException
        objs[0] = new Object();
        
        // 编译错误：Type mismatch: cannot convert from Object to String
        //String[] strs = {"s", "st", "str", new Object()};
    }
```




- AbstractCollection中的操作功能大多数通过迭代器实现



