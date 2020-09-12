# SortedMap

进一步提供关于键的*总体排序* 的 `Map`。

注意

- 该映射根据自然顺序或指定的Comparator排序
- 对于map的几种视图的迭代是有序的
- map提供了一些获取子map和首尾元素的方法
- 所有的key必须实现Comparable或指定Comparator，否则将抛出异常ClassCastException

```java
    static class A {}

	static void sortedMapTest() {
        SortedMap<A, String> map = new TreeMap<>();
        // 内部类A未实现Comparable或指定comparator对象
        // 抛出异常：java.lang.ClassCastException: priv.cn.navyd.MapTest$A cannot be cast to java.lang.Comparable
        map.put(new A(), "a");
        map.put(new A(), "b");
        System.out.println(map);
    }
```

TreeMap中关于key比较顺序的实现：

```java
    /**
     * Compares two keys using the correct comparison method for this TreeMap.
     */
    @SuppressWarnings("unchecked")
    final int compare(Object k1, Object k2) {
        return comparator==null ? ((Comparable<? super K>)k1).compareTo((K)k2)
            : comparator.compare((K)k1, (K)k2);
    }
```

- 提供4个标准的构造方法：`void`，`Comparator`，`Map`，`SortedMap`
- 返回的子映射的范围默认是半开区间的即`[from, to)`不包括to位置

# NavigableMap

扩展的 `SortedMap`，具有了针对给定搜索目标返回最接近匹配项的导航方法。

方法 `lowerEntry`、`floorEntry`、`ceilingEntry` 和 `higherEntry` 分别返回与小于、小于等于、大于等于、大于给定键的键关联的 `Map.Entry` 对象，如果不存在这样的键，则返回 `null`。类似地，方法 `lowerKey`、`floorKey`、`ceilingKey` 和 `higherKey` 只返回关联的键。

注意

- 所有这些方法是为查找条目而不是遍历条目而设计的。

- 可以按照键的升序或降序访问和遍历 `NavigableMap`，降序表示的所有关系方法和方向方法都是逆向的。升序（默认）操作和视图的性能可能比降序更好

- 所有的submap子映射类型的方法返回值的类型为SortedMap，但是具体实现必须为NavigableMap类型

  ​