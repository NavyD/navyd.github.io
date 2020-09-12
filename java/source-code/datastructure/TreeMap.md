# TreeMap #

基于红黑树（Red-Black tree）的 NavigableMap 实现。该映射根据其键的自然顺序进行排序，或者根据创建映射时提供的 Comparator 进行排序，具体取决于使用的构造方法。此实现为 containsKey、get、put 和 remove 操作提供受保证的 log(n) 时间开销。
这些算法是 Cormen、Leiserson 和 Rivest 的 Introduction to Algorithms 中的算法的改编。 

关于TreeMap中红黑树：TreeMap红黑树分析

TreeMap的继承实现结构

    public class TreeMap<K,V>
    extends AbstractMap<K,V>
    implements NavigableMap<K,V>, Cloneable, java.io.Serializable

TreeMap<K,V>：TreeMap是以key-value形式存储数据的。

extends AbstractMap<K,V>：继承了AbstractMap，实现Map接口时需要实现的工作量大大减少了。

implements NavigableMap：实现了NavigableMap，可以返回特定条件最近匹配的导航方法。方法 lowerEntry、floorEntry、ceilingEntry 和 higherEntry 分别返回与小于、小于等于、大于等于、
大于给定键的键关联的 Map.Entry 对象，如果不存在这样的键，则返回 null。

implements Cloneable：表明其可以调用clone()方法来返回实例的field-for-field拷贝。

implements Serializable：表明该类是可以序列化的。

**主要字段：**
    
    /**
     * treeMap的排序规则，如果为null，则根据键的自然顺序进行排序
     */
    private final Comparator<? super K> comparator;
    
    /**
     * 红黑数的根节点
     */
    private transient Entry<K,V> root;
    
    /**
     * 红黑树节点的个数
     */
    private transient int size = 0;
    
    /**
     * treeMap的结构性修改次数。实现fast-fail机制的关键。
     */
    private transient int modCount = 0;

    /**
     * 视图只有在第一次请求时创建并只创建一个
     */
    private transient EntrySet entrySet;
    private transient KeySet<K> navigableKeySet;
    private transient NavigableMap<K,V> descendingMap;




**构造方法：**

- TreeMap()：使用key的自然排序来构造一个空的treeMap。
- TreeMap(Comparator<? super K> comparator)：使用给定的比较器来构造一个空的treeMap。
- TreeMap(Map<? extends K, ? extends V> m)：使用key的自然排序来构造一个treeMap，treeMap包含给定map中所有的键值对。
    `public TreeMap(Map<? extends K, ? extends V> m) {
        comparator = null;
        putAll(m);
    }`
- TreeMap(SortedMap<K, ? extends V> m)：使用指定的sortedMap来构造treeMap。treeMap中含有sortedMap中所有的键值对，键值对顺序和sortedMap中相同。使用一个有序的map构造新的treemap。这个方法需要线性时间

**主要方法：**

get方法：

     /**
     * 通用二叉树的查找算法。提供log2(n)的复杂度
     * @param key
     * @return
     */
    final Entry<K,V> getEntry(Object key) {
        // Offload comparator-based version for sake of performance
    	// 直接使用指定的比较器查找
        if (comparator != null)
            return getEntryUsingComparator(key);// 与当前方法类似，只是使用compare(o1,o2)比较
        // 不允许null
        if (key == null)
            throw new NullPointerException();
        @SuppressWarnings("unchecked")
        Comparable<? super K> k = (Comparable<? super K>) key;
        Entry<K,V> p = root;
        // 查找
        while (p != null) {
            int cmp = k.compareTo(p.key);
            // key小于当前节点取左节点比较
            if (cmp < 0)
                p = p.left;
            // key大于当前节点取右节点比较
            else if (cmp > 0)
                p = p.right;
            // 找到
            else
                return p;
        }
        // 没有找到
        return null;
    }

     /**
     * 返回大于等于key的最小键。如果不存在就返回null。
     * 算法：
     * 1.如果key < 当前节点p，寻找左子树，若左子树不存在，p就是最小大于key的
     * 2.如果key > 当前节点p，寻找右子树，若右子树不存在，需要向上回溯第一个大于key的键
     * 即key < 节点p，使用左链接(一个大于等于key的键的左子树中不存在更小的大于等于key的键)
     * @param key
     * @return
     */
    final Entry<K,V> getCeilingEntry(K key) {
        Entry<K,V> p = root;
        while (p != null) {
        	// 静态方法，比较器comparator为空就是用默认的比较
            int cmp = compare(key, p.key);
            // key比当前节点小
            if (cmp < 0) {
            	// 当前节点存在更小的子节点
                if (p.left != null)
                    p = p.left;
                // 没有更小的子节点，当前节点就是树中最小大于key的节点
                else
                    return p;
            } 
            // key比当前节点大
            else if (cmp > 0) {
            	// 当前节点存在更大的子节点
                if (p.right != null) {
                    p = p.right;
                }
                // 当前节点没有更大的节点能大于key，即子树中不存在大于key的键。只能向上回溯第一个使用左链接比较的节点
                // 即当一个节点p大于key时，仍然在左子树中寻找小于p大于key的键，那么第一个左链接节点必定是最小大于key的
                else {
                    Entry<K,V> parent = p.parent;
                    Entry<K,V> ch = p;
                    // parent.left连接时退出循环或不存在大于等于key的键
                    while (parent != null && ch == parent.right) {
                        ch = parent;
                        parent = parent.parent;
                    }
                    return parent;
                }
            } 
            // 找到key相等节点p
            else
                return p;
        }
        return null;
    }

     /**
     * 取小于等于key的最大键。遇到第一个key.compareTo(p) > 0的就会到右子树中取最小值
     * 算法：
     * 1.如果key < 当前节点p，若p的左子树存在，就查找左子树，如果不存在，就回溯找第一个小于key的键
     * 即k > 节点p，使用右连接的父节点(原理是当一个节点小于key，就会查找右子树是否有大一点的节点小于key)
     * 2.如果key > 当前节点p，寻找右子树，若右子树不存在就返回p最小大于等于key的
     * @param key
     * @return
     */
    final Entry<K,V> getFloorEntry(K key) {
        Entry<K,V> p = root;
        while (p != null) {
            int cmp = compare(key, p.key);
            // key比当前节点大
            if (cmp > 0) {
                if (p.right != null)
                    p = p.right;
                // 找不到比key更大的键，就返回当前键是小于key的最大键
                else
                    return p;
            } 
            // key比当前节点小
            else if (cmp < 0) {
                if (p.left != null) {
                    p = p.left;
                } 
                // 找不到
                else {
                	// 如果左子树中不存在跟接近key的节点就返回第一个右链接的父节点
                    Entry<K,V> parent = p.parent;
                    Entry<K,V> ch = p;
                    // 当parent使用右链接时退出循环或不存在小于等于key的键
                    while (parent != null && ch == parent.left) {
                        ch = parent;
                        parent = parent.parent;
                    }
                    return parent;
                }
            } 
            // 相等
            else
                return p;

        }
        return null;
    }

put方法：

     /**
     * 在map中关联指定的键值对。不允许插入null。只对插入操作进行红黑树修复。提供log(n)复杂度
     */
    public V put(K key, V value) {
        Entry<K,V> t = root;
        // 根节点为null就直接插入新键
        if (t == null) {
            compare(key, key); // type (and possibly null) check

            root = new Entry<>(key, value, null);
            size = 1;
            modCount++;
            return null;
        }
        // 引用放在循环外。是否感觉可以改善自己的代码啦啦？？？等到知道具体机制可能就不会这样想了。手动滑稽
        int cmp;
        Entry<K,V> parent;
        // split comparator and comparable paths
        Comparator<? super K> cpr = comparator;
        // 使用比较器查找到key进行替换操作
        if (cpr != null) {
            do {
                parent = t;
                cmp = cpr.compare(key, t.key);
                if (cmp < 0)
                    t = t.left;
                else if (cmp > 0)
                    t = t.right;
                // 相等就直接替换值
                else
                    return t.setValue(value);
            } while (t != null);
        }
        // 使用默认的顺序查找到key进行替换操作
        else {
        	// 不允许为null
            if (key == null)
                throw new NullPointerException();
            @SuppressWarnings("unchecked")
                Comparable<? super K> k = (Comparable<? super K>) key;
            do {
                parent = t;
                cmp = k.compareTo(t.key);
                if (cmp < 0)
                    t = t.left;
                else if (cmp > 0)
                    t = t.right;
                else
                    return t.setValue(value);
            } while (t != null);
        }
        // 将新节点插入到父节点
        Entry<K,V> e = new Entry<>(key, value, parent);
        // 判断父节点应用哪个连接新节点
        if (cmp < 0)
            parent.left = e;
        else
            parent.right = e;
        // 修复操作
        fixAfterInsertion(e);
        size++;
        modCount++;
        return null;
    }

    /**
     * 将指定映射中的所有映射关系复制到此映射中。如果已经存在的映射会被替换新的值
     * 对于空treemap使用putAll提供线性时间。好于非空treemap的n*logn
     * @author Navy D
     */
    public void putAll(Map<? extends K, ? extends V> map) {
        int mapSize = map.size();
        // treemap是空的  参数map是sortedMap
        if (size==0 && mapSize!=0 && map instanceof SortedMap) {
            Comparator<?> c = ((SortedMap<?,?>)map).comparator();
            // 比较器一样为null或同一个对象
            if (c == comparator || (c != null && c.equals(comparator))) {
                ++modCount;
                try {
                	// 使用迭代器通过key构建排序数据，需要线性时间 这个方法暂时没用到就不看了，用到再更新吧
                    buildFromSorted(mapSize, map.entrySet().iterator(),
                                    null, null);
                } catch (java.io.IOException cannotHappen) {
                } catch (ClassNotFoundException cannotHappen) {
                }
                return;
            }
        }
        // abstractMap.putAll方法采用for调用put方法
        super.putAll(map);
    }

delete方法：

     /**
     * 在map中删除指定的键和关联的值
     */
    public V remove(Object key) {
    	// 查找
        Entry<K,V> p = getEntry(key);
        if (p == null)
            return null;

        V oldValue = p.value;
        // 删除键值对
        deleteEntry(p);
        return oldValue;
    }

     /**
     * 删除节点p且平衡树
     * 对于有两个子节点的删除节点p，使用右子树的最小节点替换，
     * 然后根据这个最小节点是叶子结点就先修复再删除，若有一个右子树就使用右子树中节点与父节点连接
     * 对于有一个子节点的删除节点p，使用删除节点的子节点与父节点连接
     * 对于没右子节点就修复后再删除
     * @param p
     */
    private void deleteEntry(Entry<K,V> p) {
        modCount++;
        size--;
        // If strictly internal, copy successor's element to p and then make p
        // point to successor.
        // 待删除结点有两个孩子用中序后继覆盖删除节点
        if (p.left != null && p.right != null) {
        	// 返回p的右子树中的最小节点
            Entry<K,V> s = successor(p);
            // 将后继的键值覆盖删除点p的键值  没有更换颜色
            p.key = s.key;
            p.value = s.value;
            // 将p引用为后继节点 注意不是覆盖到删除节点 删除点p已经被替换为后继
            p = s;
        } // p has 2 children

        // Start fixup at replacement node, if it exists.
        // 如果删除节点只有一个孩子就返回这个孩子。注意如果进入上一个if，返回的p如果是叶节点，即replacement=null
        // p如果不是叶节点，只会存在右子节点
        Entry<K,V> replacement = (p.left != null ? p.left : p.right);
        // 删除节点存在一个子节点(左或右)，父节点链接删除节点的子节点
        if (replacement != null) {
            // Link replacement to parent
        	// 连接p的父节点与替换节点  删除p
            replacement.parent = p.parent;
            if (p.parent == null)
                root = replacement;
            // 替换父节点的左链接
            else if (p == p.parent.left)
                p.parent.left  = replacement;
            // 替换右链接
            else
                p.parent.right = replacement;

            // Null out links so they are OK to use by fixAfterDeletion.
            p.left = p.right = p.parent = null;

            // Fix replacement
            // 只有删除点是BLACK的时候，才会触发删除修复，因为删除RED节点不会破坏红黑树的任何约束，而删除BLACK节点会导致有不同个数的黑色节点
            if (p.color == BLACK)
                fixAfterDeletion(replacement);
        }
        // 只有root一个节点
        else if (p.parent == null) { // return if we are the only node.
            root = null;
        }
        // 没有孩子节点 p是叶子结点
        else { //  No children. Use self as phantom replacement and unlink.
            if (p.color == BLACK)
                fixAfterDeletion(p);
            // 将连接删除
            if (p.parent != null) {
                if (p == p.parent.left)
                    p.parent.left = null;
                else if (p == p.parent.right)
                    p.parent.right = null;
                p.parent = null;
            }
        }
    }

iterator方法：初步看了一下源码，类有点多，等到需要时再更新吧


----------

first_edited_20171016