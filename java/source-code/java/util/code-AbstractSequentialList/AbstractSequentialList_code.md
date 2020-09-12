# AbstractSequentialList

此类提供了 List 接口的骨干实现，从而最大限度地减少了实现受“连续访问”数据存储（如链接列表）支持的此接口所需的工作。对于随机访问数据（如数组），应该优先使用 AbstractList，而不是先使用此类。

类结构：

```java
public abstract class AbstractSequentialList<E> extends AbstractList<E> 
```

![](images/abstractsequentiallist_1.png)

注意

- AbstractSequentialList相对AbstractList增加了抽象方法和Unsupported方法的默认实现，而这些增加的默认的实现都有一个特点，**主要通过列表迭代器ListIterator实现**，用户只需要实现迭代器就可以创建List．即唯一的一个抽象方法` public abstract ListIterator<E> listIterator(int index);`



## 抽象方法

- public abstract ListIterator<E> listIterator(int index);



注意：如果直接继承该类，还会要求实现一个方法`public int size()`，该方法从java.util.Collection接口而来，其中所有的抽象类都将该方法下放到具体类实现

## 实现方法

具体的源码请找对应的源码文件，这些实现都借助于ListIterator完成调用