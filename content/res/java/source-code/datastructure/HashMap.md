# HashMap #

**摘要**

HashMap是Java程序员使用频率最高的用于映射(键值对)处理的数据类型。随着JDK（Java Developmet Kit）版本的更新，JDK1.8对HashMap底层的实现进行了优化，例如引入红黑树的数据结构和扩容的优化等。本文结合JDK1.7和JDK1.8的区别，深入探讨HashMap的结构实现和功能原理。

**简介**

Java为数据结构中的映射定义了一个接口java.util.Map，此接口主要有四个常用的实现类，分别是HashMap、Hashtable、LinkedHashMap和TreeMap，类继承关系如下图所示：

![](https://pic2.zhimg.com/26341ef9fe5caf66ba0b7c40bba264a5_r.jpg)

下面针对各个实现类的特点做一些说明：

(1) HashMap：它根据键的hashCode值存储数据，大多数情况下可以直接定位到它的值，因而具有很快的访问速度，但遍历顺序却是不确定的。 HashMap最多只允许一条记录的键为null，允许多条记录的值为null。HashMap非线程安全，即任一时刻可以有多个线程同时写HashMap，可能会导致数据的不一致。如果需要满足线程安全，可以用 Collections的synchronizedMap方法使HashMap具有线程安全的能力，或者使用ConcurrentHashMap。

(2) Hashtable：Hashtable是遗留类，很多映射的常用功能与HashMap类似，不同的是它承自Dictionary类，并且是线程安全的，任一时间只有一个线程能写Hashtable，并发性不如ConcurrentHashMap，因为ConcurrentHashMap引入了分段锁。Hashtable不建议在新代码中使用，不需要线程安全的场合可以用HashMap替换，需要线程安全的场合可以用ConcurrentHashMap替换。

(3) LinkedHashMap：LinkedHashMap是HashMap的一个子类，保存了记录的插入顺序，在用Iterator遍历LinkedHashMap时，先得到的记录肯定是先插入的，也可以在构造时带参数，按照访问次序排序。

(4) TreeMap：TreeMap实现SortedMap接口，能够把它保存的记录根据键排序，默认是按键值的升序排序，也可以指定排序的比较器，当用Iterator遍历TreeMap时，得到的记录是排过序的。如果使用排序的映射，建议使用TreeMap。在使用TreeMap时，key必须实现Comparable接口或者在构造TreeMap传入自定义的Comparator，否则会在运行时抛出java.lang.ClassCastException类型的异常。

对于上述四种Map类型的类，要求映射中的key是不可变对象。不可变对象是该对象在创建后它的哈希值不会被改变。如果对象的哈希值发生变化，Map对象很可能就定位不到映射的位置了。

通过上面的比较，我们知道了HashMap是Java的Map家族中一个普通成员，鉴于它可以满足大多数场景的使用条件，所以是使用频度最高的一个。下文我们主要结合源码，从存储结构、常用方法分析、扩容以及安全性等方面深入讲解HashMap的工作原理。

**hashMap的数据结构：**

HashMap 是一个采用哈希表实现的键值对集合，继承自 AbstractMap，实现了 Map 接口 。 
HashMap 的特殊存储结构使得在获取指定元素前需要经过**hash运算**，*得到目标元素在哈希表中的位置*，然后再进行少量比较即可得到元素，这使得 HashMap 的查找效率很高。

HashMap采用了链地址法。链地址法，简单来说，就是数组加链表的结合。在每个数组元素上都一个链表结构，当数据被Hash后，得到数组下标，把数据放在对应下标元素的链表上。

当发生 哈希冲突（碰撞）的时候，HashMap 采用 拉链法 进行解决，因此 HashMap 的底层实现是 **数组+链表+红黑树**，如下图 所示

![](https://pic1.zhimg.com/8db4a3bdfb238da1a1c4431d2b6e075c_b.png)

hashmap结构：

    public class HashMap<K,V> extends AbstractMap<K,V>
    implements Map<K,V>, Cloneable, Serializable {

主要字段：

     //默认初始容量为16
    static final int DEFAULT_INITIAL_CAPACITY = 1 << 4; // aka 16
       
     //默认最大容量为2^30
    static final int MAXIMUM_CAPACITY = 1 << 30; 
    
    // 默认加载因子：最大存储元素数量threshold/table数组长度 = loadfactor
    static final float DEFAULT_LOAD_FACTOR = 0.75f;
    
    //碰撞拉链法链表长度超过8就转为红黑树存储
    static final int TREEIFY_THRESHOLD = 8;
    
    // 在红黑树的元素少于6时转变为普通的链表
    static final int UNTREEIFY_THRESHOLD = 6;

    // 链表转换为红黑树需要table数组至少为64
    static final int MIN_TREEIFY_CAPACITY = 64;

    // hash数组 第一次被使用时初始化，默认大小为2^4,需要时调整大小，长度为2的幂。在一些操作中允许长度为0
    transient Node<K,V>[] table;
    
    // HashMap中当前的键值对数量
    transient int size; 
    
    //modCount字段主要用来记录HashMap内部结构发生变化的次数，主要用于迭代的快速失败 如put新键值对
    transient int modCount;
    
    // 所能容纳的key-value对极限  threshold = length * Load factor
    int threshold;
    
    // 负载因子 这个值可以大于1 默认为0.75
    final float loadFactor;




    
内部类：

    // 单向链表
    static class Node<K,V> implements Map.Entry<K,V> {
    	//用来定位数组索引位置
        final int hash;
        final K key;
        V value;
      //链表的下一个node
        Node<K,V> next;

        Node(int hash, K key, V value, Node<K,V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }

     /**
     * 红黑树节点
     */
    static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
        TreeNode<K,V> parent;  // red-black tree links
        TreeNode<K,V> left;
        TreeNode<K,V> right;
        TreeNode<K,V> prev;    // needed to unlink next upon deletion
        boolean red;
        TreeNode(int hash, K key, V val, Node<K,V> next) {
            super(hash, key, val, next);
        }

注意：TreeNode类继承自 LinkedHashMap.Entry ，而 LinkedHashMap.Entry 继承自 HashMap.Node (自身单向链表类)还有额外的 6 个属性：

    //继承 LinkedHashMap.Entry 的
    Entry before, after;
    
    //HashMap.Node 的
    final int hash;
    final K key;
    V value;
    Node next;





Static utilities methods:

     /**
     * 扰动函数,对于不是素数容量(table.length为2的幂)和浮点数采用按位异或保留高位的信息
     * 常规的设计是把桶的大小设计为素数。相对来说素数导致冲突的概率要小于合数.HashMap采用这种非常规设计，
     * 主要是为了在取模和扩容时做优化，同时为了减少冲突
     * @param key
     * @return
     */
    static final int hash(Object key) {
        int h;
        // 											高位参与运算
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }
具体的按位异或运算如图：
![](https://pic2.zhimg.com/8e8203c1b51be6446cda4026eaaccf19_b.png)

    //取接近指定参数 cap 的 2的幂hash数组table容量。假如你传入的是 5，返回的初始容量为 8
    static final int tableSizeFor(int cap) {
        int n = cap - 1;
        // 将最高有效位为1后面的所有位都置1
        n |= n >>> 1;
        n |= n >>> 2;
        n |= n >>> 4;
        n |= n >>> 8;
        n |= n >>> 16;
        // 	可能溢出
        return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
    }


主要方法：

get:

    /**
     * 使用key和其hash值判断是否与某个节点相等
     */
    final Node<K,V> getNode(int hash, Object key) {
        Node<K,V>[] tab; Node<K,V> first, e; int n; K k;
        // 取出表中hash位置的Node
        if ((tab = table) != null && (n = tab.length) > 0 &&
            (first = tab[(n - 1) & hash]) != null) {// hash位置的节点不为null
        	// key与这个节点桶位相等
        	if (first.hash == hash && // always check first node
                ((k = first.key) == key || (key != null && key.equals(k))))
                return first;
        	// 这个桶位存在链表或树
            if ((e = first.next) != null) {
            	// 红黑树get
                if (first instanceof TreeNode)
                    return ((TreeNode<K,V>)first).getTreeNode(hash, key);
                // 链表遍历get
                do {
                    if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                        return e;
                } while ((e = e.next) != null);
            }
        }
        return null;
    }

    /**
     * 遍历所有节点匹配值。提供n^2的复杂度
     */
    public boolean containsValue(Object value) {
        Node<K,V>[] tab; V v;
        // table数组存在元素
        if ((tab = table) != null && size > 0) {
        	// 遍历所有节点
            for (int i = 0; i < tab.length; ++i) {
                for (Node<K,V> e = tab[i]; e != null; e = e.next) {
                    if ((v = e.value) == value ||
                        (value != null && value.equals(v)))
                        return true;
                }
            }
        }
        return false;
    }


put：

    /**
     * 向map中插入键值对
     * 如果key存在hash表中，就返回旧值，否则返回null
     * @return
     */
    final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                   boolean evict) {
		//tab为node原数组的引用，p为node中的key元素，n为数组长度，i为key的hash下标
        Node<K,V>[] tab; Node<K,V> p; int n, i;
		// 数组table是为空或长度为0，执行resize()新建一个table数组
        if ((tab = table) == null || (n = tab.length) == 0)
            n = (tab = resize()).length;
		//计算key的hash值的数组索引i，如果桶位i没有元素，直接新建节点添加
        if ((p = tab[i = (n - 1) & hash]) == null)
            tab[i] = newNode(hash, key, value, null);
		// 桶位table[i]不为空，
        else {
        	// e表示存在于key相同的键的节点，k是数组中hash位置的第一个node的键
            Node<K,V> e; K k;
			// 键key与桶位p节点相等 就赋值给e。其中key可能为null就多设置一个条件
            if (p.hash == hash &&
                ((k = p.key) == key || (key != null && key.equals(k))))//相同指的是hashCode以及equals
                e = p;
			// 是红黑树，在树中插入键值对
            else if (p instanceof TreeNode)
                e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
			// p是链表 插入链表
            else {
                for (int binCount = 0; ; ++binCount) {
					//如果下一个是null，就插入
                    if ((e = p.next) == null) {
                        p.next = newNode(hash, key, value, null);
						//链表长度大于等于8的话把链表转换为红黑树
                        if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                            treeifyBin(tab, hash);
                        break;
                    }
					//遍历过程中若发现key已经存在直接退出循环
                    if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                        break;
                    p = e;
                }
            }
			//存在替换节点e  与key相同直接覆盖value
            if (e != null) { // existing mapping for key
                V oldValue = e.value;
				//如果允许更改存在的key，或原值为null
                if (!onlyIfAbsent || oldValue == null)
                    e.value = value;
               // linkedHashMap实现方法
                afterNodeAccess(e);
                return oldValue;
            }
        }
        ++modCount;
		//判断实际存在的键值对数量size是否超多了最大容量threshold，如果超过，进行扩容。
        if (++size > threshold)
            resize();
        // linkedHashMap实现方法
        afterNodeInsertion(evict);
        return null;
    }

put方法的步骤：

![](https://pic3.zhimg.com/58e67eae921e4b431782c07444af824e_b.png)


remove:

    /**
     * 删除指定的键值对
     */
    final Node<K,V> removeNode(int hash, Object key, Object value,
                               boolean matchValue, boolean movable) {
        Node<K,V>[] tab; Node<K,V> p; int n, index;
        // 在table数组中找到这个key节点所属的桶位节点不为null
        if ((tab = table) != null && (n = tab.length) > 0 &&
            (p = tab[index = (n - 1) & hash]) != null) {
            Node<K,V> node = null, e; K k; V v;
            // 如果table[hash]桶位节点与这个key表示的对象相等
            if (p.hash == hash &&
                ((k = p.key) == key || (key != null && key.equals(k))))
                node = p;
            // 有链表存在
            else if ((e = p.next) != null) {
            	// 红黑树get这个节点
            	if (p instanceof TreeNode)
                    node = ((TreeNode<K,V>)p).getTreeNode(hash, key);
                // 链表遍历寻找这个节点
            	else {
                    do {
                    	// 相等
                        if (e.hash == hash &&
                            ((k = e.key) == key ||
                             (key != null && key.equals(k)))) {
                            node = e;
                            break;
                        }
                        p = e;
                    } while ((e = e.next) != null);
                }
            }
            // 找到节点			是否匹配节点的值(默认不匹配)
            if (node != null && (!matchValue || (v = node.value) == value ||
                                 (value != null && value.equals(v)))) {
            	// 红黑树删除节点
            	if (node instanceof TreeNode)
                    ((TreeNode<K,V>)node).removeTreeNode(this, tab, movable);
            	// 链表节点  删除节点就在桶位table[hash]上
            	else if (node == p)
                    tab[index] = node.next;
            	// 删除链表中  元素改变链接
                else
                    p.next = node.next;
                ++modCount;
                --size;
                afterNodeRemoval(node);
                return node;
            }
        }
        return null;
    }


扩容resize:

    /**
     * 初始化或增大2倍容量。因为使用的table数组是2的幂，移动元素时要么保持在旧数组中的索引位置，
     * 要么就在新数组中偏移2的次幂位置。(具体在下面解释)
     * @return
     */
    final Node<K,V>[] resize() {
        Node<K,V>[] oldTab = table;
        int oldCap = (oldTab == null) ? 0 : oldTab.length;
        int oldThr = threshold;
        int newCap, newThr = 0;
        // 对老数组扩容
        if (oldCap > 0) {
			//超过最大值就不再扩充了
            if (oldCap >= MAXIMUM_CAPACITY) {
                threshold = Integer.MAX_VALUE;
                return oldTab;
            }
            // 没超过最大值，数组容量扩充为原来的2倍，如果老的容量不小于16就将元素最大限制扩充为原来的2倍
            else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                     oldCap >= DEFAULT_INITIAL_CAPACITY)
                newThr = oldThr << 1; // double threshold
        }
        // 旧容量=0且旧阀值>0说明创建了hashmap但没有put resize初始化， 使用指定的threshold(2的幂)初始化数组容量
        else if (oldThr > 0) // initial capacity was placed in threshold
            newCap = oldThr;
        // 构造时没有指定任何东西，使用默认的创建数组
        else {               // zero initial threshold signifies using defaults
            newCap = DEFAULT_INITIAL_CAPACITY;
            newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
        }
        // 针对只指定threshold(默认构造器)使用指定阀值创建数组，新阀值为 容量*加载因子
        if (newThr == 0) {
            float ft = (float)newCap * loadFactor;
            newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                      (int)ft : Integer.MAX_VALUE);
        }
        // 更新阀值
        threshold = newThr;
        // 新容量数组
        @SuppressWarnings({"rawtypes","unchecked"})
        Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
        table = newTab;
        // 移动老数组中元素到新数组
        if (oldTab != null) {
        	// 把每个旧的bucket都移动到新的bucket中
            for (int j = 0; j < oldCap; ++j) {
                Node<K,V> e;
                if ((e = oldTab[j]) != null) {
                	// 删除旧数组的值
                    oldTab[j] = null;
                    // 没有链表，只有 一个元素
                    if (e.next == null)
                        newTab[e.hash & (newCap - 1)] = e;
                    // 如果是红黑树
                    else if (e instanceof TreeNode)
                        ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                    // 优化链表
                    else { // preserve order
                        Node<K,V> loHead = null, loTail = null;
                        Node<K,V> hiHead = null, hiTail = null;
                        Node<K,V> next;
                        // 计算链表中元素索引 并保存元素原来的顺序
                        do {
                            next = e.next;
                            /**
                             * 使用的是2次幂的扩展(指长度扩为原来2倍)，所以，元素的位置要么是在原位置，
                             * 要么是在原位置再移动2次幂的位置。如原数组容量为16:0001 0000
                             * 新容量为0010 0000,在扩容之前使用的是key的低4位信息与0000 1111(15)位与
                             * 如果在key的第5位是1就在新数组的位置为 原索引+oldCap，如果是0就与之前的不变
                             * 如:key=0101 0101.在16数组中是5位置，在32数组中是21=5+16位置
                             */
                            // 节点key新的位数为0 使原索引位置保持原来有序
                            if ((e.hash & oldCap) == 0) {
                                if (loTail == null)
                                    loHead = e;
                                else
                                    loTail.next = e;
                                loTail = e;
                            }
                            // 节点key新的位数为1 使新索引位置保持原来有序
                            else {
                                if (hiTail == null)
                                    hiHead = e;
                                else
                                    hiTail.next = e;
                                hiTail = e;
                            }
                        } while ((e = next) != null);
                        // lo在原索引位置上连接新链表
                        if (loTail != null) {
                            loTail.next = null;
                            newTab[j] = loHead;
                        }
                        // hi在新索引位置连接链表
                        if (hiTail != null) {
                            hiTail.next = null;
                            // 新索引位置 原索引+oldCap
                            newTab[j + oldCap] = hiHead;
                        }
                    }
                }
            }
        }
        // 返回新数组
        return newTab;
    }

新旧数组链表移动位置优化：

经过观测可以发现，我们使用的是2次幂的扩展(指长度扩为原来2倍)，所以，元素的位置要么是在原位置，要么是在原位置再移动2次幂的位置。看下图可以明白这句话的意思，n为table的长度，图（a）表示扩容前的key1和key2两种key确定索引位置的示例，图（b）表示扩容后key1和key2两种key确定索引位置的示例，其中hash1是key1对应的哈希与高位运算结果。
![](https://pic2.zhimg.com/a285d9b2da279a18b052fe5eed69afe9_b.png)

元素在重新计算hash之后，因为n变为2倍，那么n-1的mask范围在高位多1bit(红色)，因此新的index就会发生这样的变化：
![](https://pic2.zhimg.com/b2cb057773e3d67976c535d6ef547d51_b.png)

因此，我们在扩充HashMap的时候，不需要像JDK1.7的实现那样重新计算hash，只需要看看原来的hash值新增的那个bit是1还是0就好了，是0的话索引没变，是1的话索引变成“原索引+oldCap”，可以看看下图为16扩充为32的resize示意图：
![](https://pic3.zhimg.com/544caeb82a329fa49cc99842818ed1ba_b.png)

这个设计确实非常的巧妙，既省去了重新计算hash值的时间，而且同时，由于新增的1bit是0还是1可以认为是随机的，因此resize的过程，均匀的把之前的冲突的节点分散到新的bucket了。这一块就是JDK1.8新增的优化点。有一点注意区别，JDK1.7中rehash的时候，旧链表迁移新链表的时候，如果在新表的数组索引位置相同，则链表元素会倒置，但是从上图可以看出，JDK1.8不会倒置。


HashMap中红黑树相关操作：

桶的树形化(链表转换为红黑树)：一个桶中的元素个数超过 TREEIFY_THRESHOLD(默认是 8 )，就使用红黑树来替换链表

    /**
	 * 如果table数组长度大于树形化最小限制MIN_TREEIFY_CAPACITY
	 * 将node链表数组中hash的链表转换为红黑树 否则就将table数组扩容
	 * @param tab
	 * @param hash
	 */
	final void treeifyBin(Node<K, V>[] tab, int hash) {
		int n, index;

		Node<K, V> e;
		// 如果table数组长度小于64不会转为红黑树，而是继续扩容
		if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
			resize();
		// 转为红黑树   	桶位链表头结点
		else if ((e = tab[index = (n - 1) & hash]) != null) {
			// 红黑树的头、尾节点
			TreeNode<K, V> hd = null, tl = null;
			do {
				// 将原链表节点新建为红黑树节点
				TreeNode<K, V> p = replacementTreeNode(e, null);
				// 保持原来的顺序 hd始终为根节点
				if (tl == null)
					hd = p;
				else {
					// 保持原有的顺序
					p.prev = tl;
					tl.next = p;
				}
				tl = p;
			} while ((e = e.next) != null);
			// 将红黑树根节点替换到table中  注意：上面操作并没有设置红黑树的颜色值，现在得到的只能算是个红黑树节点的链表
			if ((tab[index] = hd) != null)
				// 将hd作为起始节点调用
				hd.treeify(tab);
		}
	}

     	/**
         * 将TreeNode节点链表转换为红黑树
         * @param tab
         */
        final void treeify(Node<K,V>[] tab) {
            TreeNode<K,V> root = null;
            for (TreeNode<K,V> x = this, next; x != null; x = next) {
                next = (TreeNode<K,V>)x.next;
                x.left = x.right = null;
                // 第一次进入 插入根节点
                if (root == null) {
                    x.parent = null;
                    // 根节点为黑色
                    x.red = false;
                    root = x;
                }
                else {
                    K k = x.key;
                    int h = x.hash;
                    Class<?> kc = null;
                    // 类似红黑树的插入算法
                    for (TreeNode<K,V> p = root;;) {
                        // ph为当前节点的hash值
                    	int dir, ph;
                        K pk = p.key;
                        // 其实类似key.compareTo(o)
                        if ((ph = p.hash) > h)
                            dir = -1;
                        else if (ph < h)
                            dir = 1;
                        // 树节点与链表节点存在hash值一样的key
                        // 检查键k实现comparable接口 若是就检查k与pk是否同一类型，不同类型直接返回0，
                        // 同类型就返回compareTo结果
                        else if ((kc == null &&
                                  (kc = comparableClassFor(k)) == null) ||
                                 (dir = compareComparables(kc, k, pk)) == 0)
                        	// 如果比较节点的哈希值、 x  
                        	// native方法，当使用唯一hashcode k<=pk返回-1否则1
                            dir = tieBreakOrder(k, pk);

                        TreeNode<K,V> xp = p;
                        // 比较x.key hash<p.hash取左空连接新节点
                        if ((p = (dir <= 0) ? p.left : p.right) == null) {
                            x.parent = xp;
                            if (dir <= 0)
                                xp.left = x;
                            else
                                xp.right = x;
                            // 插入后修复平衡  虽然这之前插入节点都是默认黑色，平衡第一就是将x.red=true
                            root = balanceInsertion(root, x);
                            break;
                        }
                    }
                }
            }
            // 确保root在table桶位第一个
            moveRootToFront(tab, root);
        }

注意：上面的treeify和下面的putTreeVal方法中的插入步骤中都有一个判断，就是对于hash值相等但不是同一个类的情况，只需要保持相对平衡即可。在正常情况中是不用考虑的。但是作为类库必须考虑各种"被虐"。不知道深入到这种细节对于自己是否有好处？？？

    	/**
         * Tie-breaking utility for ordering insertions when equal
         * hashCodes and non-comparable. We don't require a total
         * order, just a consistent insertion rule to maintain
         * equivalence across rebalancings. Tie-breaking further than
         * necessary simplifies testing a bit.
         * 
         * 用于 a 和 b 哈希值相同但是无法比较时,不要求整体有序，只需要符合规则平衡。一般不会出现这种情况
         * 若a b的类名相等 就是用唯一的hashcode判断-1或1，若不相等就是返回0  
         */
        static int tieBreakOrder(Object a, Object b) {
            int d;
            
            if (a == null || b == null ||
                (d = a.getClass().getName().
                 compareTo(b.getClass().getName())) == 0)
                d = (System.identityHashCode(a) <= System.identityHashCode(b) ?
                     -1 : 1);
            return d;
        }

    	 /**
         * 如果树中存在旧的键值对，就返回这个节点，在put方法中替换这个节点值。否则返回null
         * Tree version of putVal.
         */
        final TreeNode<K,V> putTreeVal(HashMap<K,V> map, Node<K,V>[] tab,
                                       int h, K k, V v) {
            Class<?> kc = null;
            boolean searched = false;
            // 取根节点
            TreeNode<K,V> root = (parent != null) ? root() : this;
            for (TreeNode<K,V> p = root;;) {
                int dir, ph; K pk;
                if ((ph = p.hash) > h)
                    dir = -1;
                else if (ph < h)
                    dir = 1;
                // key与p是一个对象
                else if ((pk = p.key) == k || (k != null && k.equals(pk)))
                    return p;
                // hash值相等但不是同一个类。
                else if ((kc == null &&
                          (kc = comparableClassFor(k)) == null) ||
                         (dir = compareComparables(kc, k, pk)) == 0) {
                	// 挨个对比左右孩子  这里没仔细看！！！！！！！
                    if (!searched) {
                        TreeNode<K,V> q, ch;
                        searched = true;
                        if (((ch = p.left) != null &&
                             (q = ch.find(h, k, kc)) != null) ||
                            ((ch = p.right) != null &&
                             (q = ch.find(h, k, kc)) != null))
                        	// 如果从 ch 所在子树中可以找到要添加的节点，就直接返回
                            return q;
                    }
                    // 如果k与pk是不同类返回0，否则取唯一hash值比较返回-1或1
                    dir = tieBreakOrder(k, pk);
                }
                // 在红黑树节点插入修复
                TreeNode<K,V> xp = p;
                if ((p = (dir <= 0) ? p.left : p.right) == null) {
                    Node<K,V> xpn = xp.next;
                    TreeNode<K,V> x = map.newTreeNode(h, k, v, xpn);
                    // 红黑树连接
                    if (dir <= 0)
                        xp.left = x;
                    else
                        xp.right = x;
                    // 保持红黑树转链表时一定的连接顺序
                    // 对于有一个子节点中插入，会使新节点连接父节点，原子节点连接到新节点上
                    xp.next = x;
                    x.parent = x.prev = xp;
                    // 原子节点连接到新节点上
                    if (xpn != null)
                        ((TreeNode<K,V>)xpn).prev = x;
                    // 修复与移动
                    moveRootToFront(tab, balanceInsertion(root, x));
                    return null;
                }
            }
        }

HashMap 中往红黑树中添加一个新节点 n 时，有以下操作：

- 从根节点开始遍历当前红黑树中的元素 p，对比 n 和 p 的哈希值；
- 如果哈希值相等并且键也相等，就判断为已经有这个元素（返回值给put()方法替换值）；
- 如果哈希值就通过其他信息，比如System.identityHashCode(o)来给个大概比较结果，这里可以看到红黑树的比较并不是很准确，注释里也说了，只是保证个相对平衡即可；
- 最后得到哈希值比较结果后，如果当前节点 p 还没有左孩子或者右孩子时才能插入，否则就进入下一轮循环;
- 插入元素后还需要进行红黑树例行的平衡调整，还有确保根节点的领先地位。
> 

    	 /**
         * 使用调用者开始作为root节点向下寻找指定的hash与key的节点
         * 实际情况判断比较复杂，我想应该只需要掌握前三个判断就足够了。好吧，剩下的我都不明白！！！！
         */
        final TreeNode<K,V> find(int h, Object k, Class<?> kc) {
            TreeNode<K,V> p = this;
            do {
                int ph, dir; K pk;
                TreeNode<K,V> pl = p.left, pr = p.right, q;
                // hash小于当前节点p 取左子树
                if ((ph = p.hash) > h)
                    p = pl;
                // hash 大于当前节点p 取右子树
                else if (ph < h)
                    p = pr;
                // hash值相等，且key相等
                else if ((pk = p.key) == k || (k != null && k.equals(pk)))
                    return p;
                // hash值相等 key不等 且左子树为空 取右子树
                else if (pl == null)
                    p = pr;
                else if (pr == null)
                    p = pl;
                // hash值相等 key不等 且左右子树不为空
                else if ((kc != null ||
                          (kc = comparableClassFor(k)) != null) &&
                         (dir = compareComparables(kc, k, pk)) != 0)
                    p = (dir < 0) ? pl : pr;
                else if ((q = pr.find(h, k, kc)) != null)
                    return q;
                else
                    p = pl;
            } while (p != null);
            return null;
        }

红黑树分解split:

   		/**
         * 将一颗树分成高位和低位两颗树或树过小去树形化变为链表。
         * @param bit 通过节点hash值区分为高低位即老的容量oldCap
         */
        final void split(HashMap<K,V> map, Node<K,V>[] tab, int index, int bit) {
        	// 桶位节点即root节点
        	TreeNode<K,V> b = this;
            // Relink into lo and hi lists, preserving order
            TreeNode<K,V> loHead = null, loTail = null;
            TreeNode<K,V> hiHead = null, hiTail = null;
            int lc = 0, hc = 0;
            for (TreeNode<K,V> e = b, next; e != null; e = next) {
                next = (TreeNode<K,V>)e.next;
                // 删除链接
                e.next = null;
                // 新容量的新增bit为0  保持原来数组索引位置使用新数组lo桶位
                if ((e.hash & bit) == 0) {
                	// 保持顺序
                    if ((e.prev = loTail) == null)
                        loHead = e;
                    else
                        loTail.next = e;
                    loTail = e;
                    ++lc;
                }
                // 新容量的新增bit为1 偏移2的次幂(bit即oldCap)使用新数组hi桶位
                else {
                    if ((e.prev = hiTail) == null)
                        hiHead = e;
                    else
                        hiTail.next = e;
                    hiTail = e;
                    ++hc;
                }
            }
            // 原数组索引上
            if (loHead != null) {
            	// lo桶位元素数组小于红黑树最小容量UNTREEIFY_THRESHOLD=6 即恢复链表形式
                if (lc <= UNTREEIFY_THRESHOLD)
                    tab[index] = loHead.untreeify(map);
                // 否则 在新数组lo上作为一个新的红黑树
                else {
                    tab[index] = loHead;
                    if (hiHead != null) // (else is already treeified)
                        loHead.treeify(tab);
                }
            }
            // 新数组索引=oldIndex + offset
            if (hiHead != null) {
                if (hc <= UNTREEIFY_THRESHOLD)
                    tab[index + bit] = hiHead.untreeify(map);
                else {
                    tab[index + bit] = hiHead;
                    if (loHead != null)
                        hiHead.treeify(tab);
                }
            }
        }


----------

红黑树的删除操作就暂时不分析了。具体情况看treeMap的详细分析。写了大半天也是有点烦躁，继续写下去只会出错。

创建_10/16/2017 9:22:26 PM 

----------
**参考：**

- [https://juejin.im/entry/5839ad0661ff4b007ec7cc7a](https://juejin.im/entry/5839ad0661ff4b007ec7cc7a "面试旧敌之 HashMap : JDK 1.8 后它通过什么提升性能")
- [https://zhuanlan.zhihu.com/p/21673805](https://zhuanlan.zhihu.com/p/21673805 "Java 8系列之重新认识HashMap")

