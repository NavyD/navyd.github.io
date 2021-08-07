# LinkedHashMap #

LinkedHashMap是HashMap的直接子类，二者唯一的区别是LinkedHashMap在HashMap的基础上，采用双向链表（doubly-linked list）的形式将所有entry连接起来，这样是为保证元素的迭代顺序跟插入顺序相同。下面给出了LinkedHashMap的结构图，主体部分跟HashMap完全一样，多了header指向双向链表的头部（是一个哑元），该双向链表的迭代顺序就是entry的插入顺序。

这种结构还有一个好处：**迭代LinkedHashMap时不需要像HashMap那样遍历整个table**，而只需要**直接遍历header指向的双向链表**即可，也就是说LinkedHashMap的迭代时间就只跟entry的个数相关，而跟table的大小无关。

LinkedHashMap可以用来实现LRU算法，由于不怎么了解，暂时不怎么写关于accessorder的问题，但是遍历的问题还是能写写的

![](https://github.com/CarpenterLee/JCFInternals/raw/master/PNGFigures/LinkedHashMap_base.png)

继承结构：

    public class LinkedHashMap<K,V>
    extends HashMap<K,V>
    implements Map<K,V>

linkedhashmap大部分实现来自hashmap，所以需要结合hashmap分析源代码。

链表结构：

     static class Entry<K,V> extends HashMap.Node<K,V> {
    	// 保存插入顺序的前后链接
        Entry<K,V> before, after;
        Entry(int hash, K key, V value, Node<K,V> next) {
            super(hash, key, value, next);
        }
    }

主要字段：

    /**
     * true for access-order,false for insertion-order.
     * 所有默认未指定accessOrder字段构造器都默认使用false遍历使用插入顺序
     */
    final boolean accessOrder;

    /**
     * The head (eldest) of the doubly linked list.
     */
    // 双向链表的头结点
    transient LinkedHashMap.Entry<K,V> head;

    /**
     * The tail (youngest) of the doubly linked list.
     */
    // 双向链表的尾节点
    transient LinkedHashMap.Entry<K,V> tail;


可以注意到，源码注释上有eldest，yougest的字样，这就与accessorder这个字段有关系，如果accessorder=true，那么linkedhashmap就会**使用访问次序来保持双向链表的顺序**，最近访问的会保持在链表的尾部。对于LRU算法实现是一个很好的方式(其实我不怎么懂这个算法).

关键方法：

hashMap中有几个专门对于linkedhashmap的方法签名：

     // Callbacks to allow LinkedHashMap post-actions
    void afterNodeAccess(Node<K,V> p) { }
    void afterNodeInsertion(boolean evict) { }
    void afterNodeRemoval(Node<K,V> p) { }

这些方法体现在hashmap的方法中被调用。

如putVal 调用afterNodeAccess	afterNodeInsertion
putVal中只有当插入相同的键key更新关联值时调用afterNodeAccess，使访问到的节点被置于双向链表的尾部。
由于afterNodeInsertion默认没有作用，不讨论

replace 调用afterNodeAccess

computeIfAbsent 调用	afterNodeAccess afterNodeInsertion
虽然不知道有什么用，还是暂时贴出来吧

linkedhashmap重写版本：

     /**
     * 双向链表中删除e节点   当在hash数组和单向链表或树中删除节点e后，需要这个
     */
    void afterNodeRemoval(Node<K,V> e) { // unlink
        LinkedHashMap.Entry<K,V> p =
            (LinkedHashMap.Entry<K,V>)e, b = p.before, a = p.after;
        p.before = p.after = null;
        // p为双向链表头节点 使用下一个节点作为头结点
        if (b == null)
            head = a;
        // p不为头结点 将上一个节点的下一个连接改为p.after
        else
            b.after = a;
        // p是尾节点， 使用上一个节点作为尾部节点
        if (a == null)
            tail = b;
        // p不是尾部节点
        else
            a.before = b;
    }

    /**
     * 默认不会在插入后产生副作用(删除节点)
     * 新节点插入之后回调 ， 根据evict(hashmap中默认true)和   判断是否需要删除最老插入的节点(需要自己实现)。
     * 如果实现LruCache ？？？？？？会用到这个方法。
     */
    void afterNodeInsertion(boolean evict) { // possibly remove eldest
        LinkedHashMap.Entry<K,V> first;
        // 双向链表不为空  removeEldestEntry()方法实现为返回false 即插入不会删除节点
        if (evict && (first = head) != null && removeEldestEntry(first)) {
            K key = first.key;
            removeNode(hash(key), key, null, false, true);
        }
    }

    /**
     * 将节点e移动到链表的尾部。在newNode时已经连接head与tail
     */
    void afterNodeAccess(Node<K,V> e) { // move node to last
        LinkedHashMap.Entry<K,V> last;
        // 使用原始访问顺序 和 节点e不是原来的尾节点 (tail不可能为空 newNode时指定连接到tail)
        if (accessOrder && (last = tail) != e) {
            LinkedHashMap.Entry<K,V> p =
                (LinkedHashMap.Entry<K,V>)e, b = p.before, a = p.after;
            // 删除节点p(e)
            p.after = null;
            // p就是头结点  将头结点链接到p的下一个节点a
            if (b == null)
                head = a;
            // p不是头结点，使用p的下一个节点a应该连接到p的上一个节点
            else
                b.after = a;
            // p不是尾节点  使用p的下一个节点a前连接b
            if (a != null)
                a.before = b;
            // p是尾节点 使用p的上一个节点b作为新的尾节点
            else
                last = b;
            // 链表中只有一个节点 (a==null&&b==null才使last==null)
            if (last == null)
                head = p;
            // 链表有多个节点 将p连接到尾部
            else {
                p.before = last;
                last.after = p;
            }
            // 更新尾部指针
            tail = p;
            // 改变了链表的迭代顺序，需要快速失败检查
            ++modCount;
        }
    }

还重写了get方法：

    /**
     * 返回指定键关联的值。注意若accessorder=true会使成功访问的键被修改到链表的尾部
     */
    public V get(Object key) {
        Node<K,V> e;
        if ((e = getNode(hash(key), key)) == null)
            return null;
		// 提供访问顺序的修改
        if (accessOrder)
            afterNodeAccess(e);
        return e.value;
    }


双向链表相关：

     /**
     * 新建一个节点并连接到双向链表的尾部
     */
    Node<K,V> newNode(int hash, K key, V value, Node<K,V> e) {
        LinkedHashMap.Entry<K,V> p =
            new LinkedHashMap.Entry<K,V>(hash, key, value, e);
        // 将p节点链接到链表尾部
        linkNodeLast(p);
        return p;
    }

    /**
     * 新建一个红黑树节点并连接到双向链表的尾部
     */
    TreeNode<K,V> newTreeNode(int hash, K key, V value, Node<K,V> next) {
        TreeNode<K,V> p = new TreeNode<K,V>(hash, key, value, next);
        linkNodeLast(p);
        return p;
    }

还有一些方法没有写出来，都是覆盖hashmap中的方法以供hashmap中调用产生双向链表

迭代：
linkedHashMap很重要的一点就是迭代的方式和性能比hashmap强大不少，

containsValue:

     /**
     * 重写hashmap中的方法，由于双向链表的作用，复杂度从平方级别到O(n)线性级别
     */
    public boolean containsValue(Object value) {
        for (LinkedHashMap.Entry<K,V> e = head; e != null; e = e.after) {
            V v = e.value;
            if (v == value || (value != null && value.equals(v)))
                return true;
        }
        return false;
    }

为什么没有用双向链表重写containsKey方法呢！因为containsKey使用getNode(hash(key), key) != null判断，getNode使用散列查找自然比遍历整个链表快的多

迭代器：

    final class LinkedEntryIterator extends LinkedHashIterator
        implements Iterator<Map.Entry<K,V>> {
        public final Map.Entry<K,V> next() { return nextNode(); }
    }

    abstract class LinkedHashIterator {
        //下一个节点
        LinkedHashMap.Entry<K,V> next;
        //当前节点
        LinkedHashMap.Entry<K,V> current;
        int expectedModCount;

        LinkedHashIterator() {
            //初始化时，next 为 LinkedHashMap内部维护的双向链表的扁头
            next = head;
            //记录当前modCount，以满足fail-fast
            expectedModCount = modCount;
            //当前节点为null
            current = null;
        }
        //判断是否还有next
        public final boolean hasNext() {
            //就是判断next是否为null，默认next是head  表头
            return next != null;
        }
        //nextNode() 就是迭代器里的next()方法 。
        //该方法的实现可以看出，迭代LinkedHashMap，就是从内部维护的双链表的表头开始循环输出。
        final LinkedHashMap.Entry<K,V> nextNode() {
            //记录要返回的e。
            LinkedHashMap.Entry<K,V> e = next;
            //判断fail-fast
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
            //如果要返回的节点是null，异常
            if (e == null)
                throw new NoSuchElementException();
            //更新当前节点为e
            current = e;
            //更新下一个节点是e的后置节点
            next = e.after;
            //返回e
            return e;
        }
        //删除方法 最终还是调用了HashMap的removeNode方法
        public final void remove() {
            Node<K,V> p = current;
            if (p == null)
                throw new IllegalStateException();
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
            current = null;
            K key = p.key;
            removeNode(hash(key), key, null, false, false);
            expectedModCount = modCount;
        }
    }



----------
**参考：**

- [https://github.com/CarpenterLee/JCFInternals/blob/master/markdown/7-LinkedHashSet%20and%20LinkedHashMap.md](https://github.com/CarpenterLee/JCFInternals/blob/master/markdown/7-LinkedHashSet%20and%20LinkedHashMap.md "LinkedHashSet and LinkedHashMap")
- [http://blog.csdn.net/zxt0601/article/details/77429150](http://blog.csdn.net/zxt0601/article/details/77429150 "面试必备：LinkedHashMap源码解析（JDK8）")
- [http://blog.csdn.net/ns_code/article/details/37867985](http://blog.csdn.net/ns_code/article/details/37867985 "【Java集合源码剖析】LinkedHashmap源码剖析")

----------
10/17/2017 12:17:23 PM 

暂时停止阅读源码，必须要换个花样了，现在比较烦躁，看源码确实是一件枯燥的事，在没有动力前不会更新，先换个方式转移下注意力

10/17/2017 3:08:59 PM 

说是停止转移注意力，还是没忍住，不想看来一半的代码丢掉，坚持了下发现看懂了许多开始蛮有趣的，也许最难的不是开头和结束，而是中间那一段枯燥没有坚持罢了。

