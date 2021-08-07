# Map

将键映射到值的对象。一个映射不能包含重复的键；每个键最多只能映射到一个值。

注意

- Map提供三种视图查看映射内容： 1. 键集 2. 值集 3. 键-值映射关系集 其顺序由具体实现的迭代器保证


- 如果key为可变对象时影响了equals，映射的行为将是不确定的。
- 不允许将map本身作为key，并且当前大多数实现没有处理self-referential的场景
- map类型应该提供两个通用的构造方法：void无参和带有map类型参数的构造方法
- 作为map中的映射的key和value应该重写hashCode和equals方法，但是不应该在map中为了避免调用equals而调用hashCode

## 查询

- int size();

```java
    /**
     * Returns the number of key-value mappings in this map.  If the
     * map contains more than <tt>Integer.MAX_VALUE</tt> elements, returns
     * <tt>Integer.MAX_VALUE</tt>.
     *
     * @return the number of key-value mappings in this map
     */
	// 返回此映射中的键-值映射关系数。
    // 如果该映射包含的元素大于 Integer.MAX_VALUE，则返回 Integer.MAX_VALUE。
    int size();
```

- boolean isEmpty();

```java
  	/**
     * Returns <tt>true</tt> if this map contains no key-value mappings.
     *
     * @return <tt>true</tt> if this map contains no key-value mappings
     */
    boolean isEmpty();
```

- boolean containsKey(Object key);

```java
    /**
     * Returns <tt>true</tt> if this map contains a mapping for the specified
     * key.  More formally, returns <tt>true</tt> if and only if
     * this map contains a mapping for a key <tt>k</tt> such that
     * <tt>(key==null ? k==null : key.equals(k))</tt>.  (There can be
     * at most one such mapping.)
     *
     * @param key key whose presence in this map is to be tested
     * @return <tt>true</tt> if this map contains a mapping for the specified
     *         key
     * @throws ClassCastException if the key is of an inappropriate type for
     *         this map
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws NullPointerException if the specified key is null and this map
     *         does not permit null keys
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     */
	// 如果该map包含指定key的映射就返回true
	// 即当指定key满足(key==null ? k==null : key.equals(k))时返回true
    boolean containsKey(Object key);
```

- boolean containsValue(Object value);

```java
    /**
     * Returns <tt>true</tt> if this map maps one or more keys to the
     * specified value.  More formally, returns <tt>true</tt> if and only if
     * this map contains at least one mapping to a value <tt>v</tt> such that
     * <tt>(value==null ? v==null : value.equals(v))</tt>.  This operation
     * will probably require time linear in the map size for most
     * implementations of the <tt>Map</tt> interface.
     *
     * @param value value whose presence in this map is to be tested
     * @return <tt>true</tt> if this map maps one or more keys to the
     *         specified value
     * @throws ClassCastException if the value is of an inappropriate type for
     *         this map
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws NullPointerException if the specified value is null and this
     *         map does not permit null values
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     */
    // 如果此映射将一个或多个键映射到指定值，则返回 true
    // 即当指定value满足(value==null ? v==null : value.equals(v))时返回true
    // 这个操作在大多数实现中通常需要线性时间
    boolean containsValue(Object value);
```

## 获取

- V get(Object key);

```java
    /**
     * Returns the value to which the specified key is mapped,
     * or {@code null} if this map contains no mapping for the key.
     *
     * <p>More formally, if this map contains a mapping from a key
     * {@code k} to a value {@code v} such that {@code (key==null ? k==null :
     * key.equals(k))}, then this method returns {@code v}; otherwise
     * it returns {@code null}.  (There can be at most one such mapping.)
     *
     * <p>If this map permits null values, then a return value of
     * {@code null} does not <i>necessarily</i> indicate that the map
     * contains no mapping for the key; it's also possible that the map
     * explicitly maps the key to {@code null}.  The {@link #containsKey
     * containsKey} operation may be used to distinguish these two cases.
     *
     * @param key the key whose associated value is to be returned
     * @return the value to which the specified key is mapped, or
     *         {@code null} if this map contains no mapping for the key
     * @throws ClassCastException if the key is of an inappropriate type for
     *         this map
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws NullPointerException if the specified key is null and this map
     *         does not permit null keys
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     */
    // 返回指定键所映射的值；如果此映射不包含该键的映射关系，则返回 null。
    // 即当map满足(key==null ? k==null : key.equals(k))将返回对应的值v，否则返回null
    // 如果当前map允许null值，可以使用containkey(Object key)区分
    V get(Object key);
```

## 插入

- V put(K key, V value);

```java
    /**
     * Associates the specified value with the specified key in this map
     * (optional operation).  If the map previously contained a mapping for
     * the key, the old value is replaced by the specified value.  (A map
     * <tt>m</tt> is said to contain a mapping for a key <tt>k</tt> if and only
     * if {@link #containsKey(Object) m.containsKey(k)} would return
     * <tt>true</tt>.)
     *
     * @param key key with which the specified value is to be associated
     * @param value value to be associated with the specified key
     * @return the previous value associated with <tt>key</tt>, or
     *         <tt>null</tt> if there was no mapping for <tt>key</tt>.
     *         (A <tt>null</tt> return can also indicate that the map
     *         previously associated <tt>null</tt> with <tt>key</tt>,
     *         if the implementation supports <tt>null</tt> values.)
     * @throws UnsupportedOperationException if the <tt>put</tt> operation
     *         is not supported by this map
     * @throws ClassCastException if the class of the specified key or value
     *         prevents it from being stored in this map
     * @throws NullPointerException if the specified key or value is null
     *         and this map does not permit null keys or values
     * @throws IllegalArgumentException if some property of the specified key
     *         or value prevents it from being stored in this map
     */
    // 将指定的值与此映射中的指定键关联（可选操作）。如果此映射关系已经包含，则更新为指定的value
    // 即当且仅当 m.containsKey(k) 返回 true 时，才能说映射 m 包含键 k 的映射关系）
    V put(K key, V value);
```

- void putAll(Map<? extends K, ? extends V> m);

```java
    /**
     * Copies all of the mappings from the specified map to this map
     * (optional operation).  The effect of this call is equivalent to that
     * of calling {@link #put(Object,Object) put(k, v)} on this map once
     * for each mapping from key <tt>k</tt> to value <tt>v</tt> in the
     * specified map.  The behavior of this operation is undefined if the
     * specified map is modified while the operation is in progress.
     *
     * @param m mappings to be stored in this map
     * @throws UnsupportedOperationException if the <tt>putAll</tt> operation
     *         is not supported by this map
     * @throws ClassCastException if the class of a key or value in the
     *         specified map prevents it from being stored in this map
     * @throws NullPointerException if the specified map is null, or if
     *         this map does not permit null keys or values, and the
     *         specified map contains null keys or values
     * @throws IllegalArgumentException if some property of a key or value in
     *         the specified map prevents it from being stored in this map
     */
    // 从指定map中将所有映射关系复制到此map中
    // 等效于对指定map所有映射关系调用put(k, v)，如果此时修改了指定map将不确定操作的行为
    void putAll(Map<? extends K, ? extends V> m);
```



## 移除

- void clear();

```java
    /**
     * Removes all of the mappings from this map (optional operation).
     * The map will be empty after this call returns.
     *
     * @throws UnsupportedOperationException if the <tt>clear</tt> operation
     *         is not supported by this map
     */
    void clear();
```

- V remove(Object key);

```java
    /**
     * Removes the mapping for a key from this map if it is present
     * (optional operation).   More formally, if this map contains a mapping
     * from key <tt>k</tt> to value <tt>v</tt> such that
     * <code>(key==null ?  k==null : key.equals(k))</code>, that mapping
     * is removed.  (The map can contain at most one such mapping.)
     *
     * <p>Returns the value to which this map previously associated the key,
     * or <tt>null</tt> if the map contained no mapping for the key.
     *
     * <p>If this map permits null values, then a return value of
     * <tt>null</tt> does not <i>necessarily</i> indicate that the map
     * contained no mapping for the key; it's also possible that the map
     * explicitly mapped the key to <tt>null</tt>.
     *
     * <p>The map will not contain a mapping for the specified key once the
     * call returns.
     *
     * @param key key whose mapping is to be removed from the map
     * @return the previous value associated with <tt>key</tt>, or
     *         <tt>null</tt> if there was no mapping for <tt>key</tt>.
     * @throws UnsupportedOperationException if the <tt>remove</tt> operation
     *         is not supported by this map
     * @throws ClassCastException if the key is of an inappropriate type for
     *         this map
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws NullPointerException if the specified key is null and this
     *         map does not permit null keys
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     */
    // 如果指定key存在该map中则移除该映射关系并返回此映射中以前关联该键的值
    // 即满足(key==null ? k==null :key.equals(k))的映射关系
    // 如果此映射不包含该键的映射关系，则返回 null。如果此map允许null则不一定
    V remove(Object key);
```

## 视图

### 键集

- Set<K> keySet();

```java
    /**
     * Returns a {@link Set} view of the keys contained in this map.
     * The set is backed by the map, so changes to the map are
     * reflected in the set, and vice-versa.  If the map is modified
     * while an iteration over the set is in progress (except through
     * the iterator's own <tt>remove</tt> operation), the results of
     * the iteration are undefined.  The set supports element removal,
     * which removes the corresponding mapping from the map, via the
     * <tt>Iterator.remove</tt>, <tt>Set.remove</tt>,
     * <tt>removeAll</tt>, <tt>retainAll</tt>, and <tt>clear</tt>
     * operations.  It does not support the <tt>add</tt> or <tt>addAll</tt>
     * operations.
     *
     * @return a set view of the keys contained in this map
     */
    // 返回此映射中包含的键的 Set 视图。对映射的更改可在此 set 中反映出来
    // 如果对该 set 进行迭代的同时修改了映射（迭代器remove操作除外），则迭代结果是不确定的。
    // set不支持add和addAll操作
    Set<K> keySet();
```

### 值集

- Collection<V> values();

```java
    /**
     * Returns a {@link Collection} view of the values contained in this map.
     * The collection is backed by the map, so changes to the map are
     * reflected in the collection, and vice-versa.  If the map is
     * modified while an iteration over the collection is in progress
     * (except through the iterator's own <tt>remove</tt> operation),
     * the results of the iteration are undefined.  The collection
     * supports element removal, which removes the corresponding
     * mapping from the map, via the <tt>Iterator.remove</tt>,
     * <tt>Collection.remove</tt>, <tt>removeAll</tt>,
     * <tt>retainAll</tt> and <tt>clear</tt> operations.  It does not
     * support the <tt>add</tt> or <tt>addAll</tt> operations.
     *
     * @return a collection view of the values contained in this map
     */
    // 返回此映射中包含的值的 Collection 视图。对映射的更改可在此 collection 中反映出来
    // 如果对该collection进行迭代时修改了映射（迭代器remove操作除外），则迭代结果是不确定的。
    // 它不支持 add 或 addAll 操作。
    Collection<V> values();
```

### 键值关系集

- `Set<Map.Entry<K, V>> entrySet();`

```java
    /**
     * Returns a {@link Set} view of the mappings contained in this map.
     * The set is backed by the map, so changes to the map are
     * reflected in the set, and vice-versa.  If the map is modified
     * while an iteration over the set is in progress (except through
     * the iterator's own <tt>remove</tt> operation, or through the
     * <tt>setValue</tt> operation on a map entry returned by the
     * iterator) the results of the iteration are undefined.  The set
     * supports element removal, which removes the corresponding
     * mapping from the map, via the <tt>Iterator.remove</tt>,
     * <tt>Set.remove</tt>, <tt>removeAll</tt>, <tt>retainAll</tt> and
     * <tt>clear</tt> operations.  It does not support the
     * <tt>add</tt> or <tt>addAll</tt> operations.
     *
     * @return a set view of the mappings contained in this map
     */
    // 返回此映射中包含的映射关系的 Set 视图。对映射的更改可在此 set 中反映出来
    // 如果对该set进行迭代时修改了映射（迭代器remove操作或迭代器setValue操作）则迭代结果是不确定的。
    // 不支持 add 或 addAll 操作。
    Set<Map.Entry<K, V>> entrySet();
```

## Map.Entry

### 获取

- K getKey();

```java
        /**
         * Returns the key corresponding to this entry.
         *
         * @return the key corresponding to this entry
         * @throws IllegalStateException implementations may, but are not
         *         required to, throw this exception if the entry has been
         *         removed from the backing map.
         */
        K getKey();
```

- V getValue();

```java
        /**
         * Returns the value corresponding to this entry.  If the mapping
         * has been removed from the backing map (by the iterator's
         * <tt>remove</tt> operation), the results of this call are undefined.
         *
         * @return the value corresponding to this entry
         * @throws IllegalStateException implementations may, but are not
         *         required to, throw this exception if the entry has been
         *         removed from the backing map.
         */
        V getValue();
```

### 替换

- V setValue(V value);

```java
        /**
         * Replaces the value corresponding to this entry with the specified
         * value (optional operation).  (Writes through to the map.)  The
         * behavior of this call is undefined if the mapping has already been
         * removed from the map (by the iterator's <tt>remove</tt> operation).
         *
         * @param value new value to be stored in this entry
         * @return old value corresponding to the entry
         * @throws UnsupportedOperationException if the <tt>put</tt> operation
         *         is not supported by the backing map
         * @throws ClassCastException if the class of the specified value
         *         prevents it from being stored in the backing map
         * @throws NullPointerException if the backing map does not permit
         *         null values, and the specified value is null
         * @throws IllegalArgumentException if some property of this value
         *         prevents it from being stored in the backing map
         * @throws IllegalStateException implementations may, but are not
         *         required to, throw this exception if the entry has been
         *         removed from the backing map.
         */
        V setValue(V value);
```

### 比较和哈希

- boolean equals(Object o);

```java
        /**
         * Compares the specified object with this entry for equality.
         * Returns <tt>true</tt> if the given object is also a map entry and
         * the two entries represent the same mapping.  More formally, two
         * entries <tt>e1</tt> and <tt>e2</tt> represent the same mapping
         * if<pre>
         *     (e1.getKey()==null ?
         *      e2.getKey()==null : e1.getKey().equals(e2.getKey()))  &amp;&amp;
         *     (e1.getValue()==null ?
         *      e2.getValue()==null : e1.getValue().equals(e2.getValue()))
         * </pre>
         * This ensures that the <tt>equals</tt> method works properly across
         * different implementations of the <tt>Map.Entry</tt> interface.
         *
         * @param o object to be compared for equality with this map entry
         * @return <tt>true</tt> if the specified object is equal to this map
         *         entry
         */
        // 比较指定对象与此项的相等性。
        // 如果给定对象也是一个映射项，并且两个项表示相同的映射关系，则返回 true。
        boolean equals(Object o);
```

- `int hashCode();`

```java
        /**
         * Returns the hash code value for this map entry.  The hash code
         * of a map entry <tt>e</tt> is defined to be: <pre>
         *     (e.getKey()==null   ? 0 : e.getKey().hashCode()) ^
         *     (e.getValue()==null ? 0 : e.getValue().hashCode())
         * </pre>
         * This ensures that <tt>e1.equals(e2)</tt> implies that
         * <tt>e1.hashCode()==e2.hashCode()</tt> for any two Entries
         * <tt>e1</tt> and <tt>e2</tt>, as required by the general
         * contract of <tt>Object.hashCode</tt>.
         *
         * @return the hash code value for this map entry
         * @see Object#hashCode()
         * @see Object#equals(Object)
         * @see #equals(Object)
         */
        // 返回此映射项的哈希码值。
        int hashCode();
```





java8 新增api不熟悉  



## 比较和哈希

- boolean equals(Object o);

```java
    /**
     * Compares the specified object with this map for equality.  Returns
     * <tt>true</tt> if the given object is also a map and the two maps
     * represent the same mappings.  More formally, two maps <tt>m1</tt> and
     * <tt>m2</tt> represent the same mappings if
     * <tt>m1.entrySet().equals(m2.entrySet())</tt>.  This ensures that the
     * <tt>equals</tt> method works properly across different implementations
     * of the <tt>Map</tt> interface.
     *
     * @param o object to be compared for equality with this map
     * @return <tt>true</tt> if the specified object is equal to this map
     */
    // 比较指定的对象与此映射是否相等。
    // 如果 m1.entrySet().equals(m2.entrySet())，则两个映射 m1 和 m2 表示相同的映射关系
    // 即两个map的entry的set的大小，包含元素都相等
    boolean equals(Object o);
```

- int hashCode();

```java
    /**
     * Returns the hash code value for this map.  The hash code of a map is
     * defined to be the sum of the hash codes of each entry in the map's
     * <tt>entrySet()</tt> view.  This ensures that <tt>m1.equals(m2)</tt>
     * implies that <tt>m1.hashCode()==m2.hashCode()</tt> for any two maps
     * <tt>m1</tt> and <tt>m2</tt>, as required by the general contract of
     * {@link Object#hashCode}.
     *
     * @return the hash code value for this map
     * @see Map.Entry#hashCode()
     * @see Object#equals(Object)
     * @see #equals(Object)
     */
    // 映射的哈希码定义为此映射 entrySet() 视图中每个项的哈希码之和。
    int hashCode();
```

## 默认方法

### 获取

- default V getOrDefault(Object key, V defaultValue)

```java
    /**
     * Returns the value to which the specified key is mapped, or
     * {@code defaultValue} if this map contains no mapping for the key.
     *
     * @implSpec
     * The default implementation makes no guarantees about synchronization
     * or atomicity properties of this method. Any implementation providing
     * atomicity guarantees must override this method and document its
     * concurrency properties.
     *
     * @param key the key whose associated value is to be returned
     * @param defaultValue the default mapping of the key
     * @return the value to which the specified key is mapped, or
     * {@code defaultValue} if this map contains no mapping for the key
     * @throws ClassCastException if the key is of an inappropriate type for
     * this map
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws NullPointerException if the specified key is null and this map
     * does not permit null keys
     * (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @since 1.8
     */
    // 返回指定键的映射值，或者如果该map不包含指定键时返回defaultvalue
    default V getOrDefault(Object key, V defaultValue) {
        V v;
        // 有些map实现允许为null时使用containsKey确认
        return (((v = get(key)) != null) || containsKey(key))
            ? v
            : defaultValue;
    }
```

### 遍历

```java
    /**
     * Performs the given action for each entry in this map until all entries
     * have been processed or the action throws an exception.   Unless
     * otherwise specified by the implementing class, actions are performed in
     * the order of entry set iteration (if an iteration order is specified.)
     * Exceptions thrown by the action are relayed to the caller.
     *
     * @implSpec
     * The default implementation is equivalent to, for this {@code map}:
     * <pre> {@code
     * for (Map.Entry<K, V> entry : map.entrySet())
     *     action.accept(entry.getKey(), entry.getValue());
     * }</pre>
     *
     * The default implementation makes no guarantees about synchronization
     * or atomicity properties of this method. Any implementation providing
     * atomicity guarantees must override this method and document its
     * concurrency properties.
     *
     * @param action The action to be performed for each entry
     * @throws NullPointerException if the specified action is null
     * @throws ConcurrentModificationException if an entry is found to be
     * removed during iteration
     * @since 1.8
     */
    default void forEach(BiConsumer<? super K, ? super V> action) {
        Objects.requireNonNull(action);
        // 使用entrySet遍历
        for (Map.Entry<K, V> entry : entrySet()) {
            K k;
            V v;
            try {
                k = entry.getKey();
                v = entry.getValue();
            } catch(IllegalStateException ise) {
                // this usually means the entry is no longer in the map.
                throw new ConcurrentModificationException(ise);
            }
            action.accept(k, v);
        }
    }
```

### 替换

```java
    /**
     * Replaces each entry's value with the result of invoking the given
     * function on that entry until all entries have been processed or the
     * function throws an exception.  Exceptions thrown by the function are
     * relayed to the caller.
     *
     * @implSpec
     * <p>The default implementation is equivalent to, for this {@code map}:
     * <pre> {@code
     * for (Map.Entry<K, V> entry : map.entrySet())
     *     entry.setValue(function.apply(entry.getKey(), entry.getValue()));
     * }</pre>
     *
     * <p>The default implementation makes no guarantees about synchronization
     * or atomicity properties of this method. Any implementation providing
     * atomicity guarantees must override this method and document its
     * concurrency properties.
     *
     * @param function the function to apply to each entry
     * @throws UnsupportedOperationException if the {@code set} operation
     * is not supported by this map's entry set iterator.
     * @throws ClassCastException if the class of a replacement value
     * prevents it from being stored in this map
     * @throws NullPointerException if the specified function is null, or the
     * specified replacement value is null, and this map does not permit null
     * values
     * @throws ClassCastException if a replacement value is of an inappropriate
     *         type for this map
     *         (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws NullPointerException if function or a replacement value is null,
     *         and this map does not permit null keys or values
     *         (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws IllegalArgumentException if some property of a replacement value
     *         prevents it from being stored in this map
     *         (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws ConcurrentModificationException if an entry is found to be
     * removed during iteration
     * @since 1.8
     */
    default void replaceAll(BiFunction<? super K, ? super V, ? extends V> function) {
        Objects.requireNonNull(function);
        // 遍历
        for (Map.Entry<K, V> entry : entrySet()) {
            K k;
            V v;
            try {
                k = entry.getKey();
                v = entry.getValue();
            } catch(IllegalStateException ise) {
                // this usually means the entry is no longer in the map.
                throw new ConcurrentModificationException(ise);
            }

            // ise thrown from function is not a cme.
            v = function.apply(k, v);

            try {
                entry.setValue(v);
            } catch(IllegalStateException ise) {
                // this usually means the entry is no longer in the map.
                throw new ConcurrentModificationException(ise);
            }
        }
    }
```

### 插入

```java
    /**
     * If the specified key is not already associated with a value (or is mapped
     * to {@code null}) associates it with the given value and returns
     * {@code null}, else returns the current value.
     *
     * @implSpec
     * The default implementation is equivalent to, for this {@code
     * map}:
     *
     * <pre> {@code
     * V v = map.get(key);
     * if (v == null)
     *     v = map.put(key, value);
     *
     * return v;
     * }</pre>
     *
     * <p>The default implementation makes no guarantees about synchronization
     * or atomicity properties of this method. Any implementation providing
     * atomicity guarantees must override this method and document its
     * concurrency properties.
     *
     * @param key key with which the specified value is to be associated
     * @param value value to be associated with the specified key
     * @return the previous value associated with the specified key, or
     *         {@code null} if there was no mapping for the key.
     *         (A {@code null} return can also indicate that the map
     *         previously associated {@code null} with the key,
     *         if the implementation supports null values.)
     * @throws UnsupportedOperationException if the {@code put} operation
     *         is not supported by this map
     *         (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws ClassCastException if the key or value is of an inappropriate
     *         type for this map
     *         (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws NullPointerException if the specified key or value is null,
     *         and this map does not permit null keys or values
     *         (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @throws IllegalArgumentException if some property of the specified key
     *         or value prevents it from being stored in this map
     *         (<a href="{@docRoot}/java/util/Collection.html#optional-restrictions">optional</a>)
     * @since 1.8
     */
    default V putIfAbsent(K key, V value) {
        V v = get(key);
        if (v == null) {
            v = put(key, value);
        }

        return v;
    }
```

