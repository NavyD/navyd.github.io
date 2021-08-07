# 对联合主键索引和 InnoDB 索引组织表的理解

## 问题

有这么一个表，表结构定义类似这样的：

```sql
CREATE TABLE `geek` (
    `a` int(11) NOT NULL,
    `b` int(11) NOT NULL,
    `c` int(11) NOT NULL,
    `d` int(11) NOT NULL,
    PRIMARY KEY (`a`, `b`),
    KEY `c` (`c`),
    KEY `ca` (`c`, `a`),
    KEY `cb` (`c`, `b`)
) ENGINE = InnoDB;
```

由于历史原因，这个表需要 a、b 做联合主键，既然主键包含了 a、b 这两个字段，那意味着单独在字段 c 上创建一个索引，就已经包含了三个字段了呀，为什么要创建`ca`, `cb`这两个索引？

同事告诉他，是因为他们的业务里面有这样的两种语句：

```sql
select * from geek where c=N order by a limit 1;
select * from geek where c=N order by b limit 1;
```

我给你的问题是，这位同事的解释对吗，为了这两个查询模式，这两个索引是否都是必须的？为什么呢？

## 答案

表记录：

| a   | b   | c   | d   |
| --- | --- | --- | --- |
| 1   | 2   | 3   | d   |
| 1   | 3   | 2   | d   |
| 1   | 4   | 3   | d   |
| 2   | 1   | 3   | d   |
| 2   | 2   | 2   | d   |
| 2   | 3   | 4   | d   |

主键 ab 的聚簇索引组织顺序相当于 order by a,b ，也就是先按 a 排序，再按 b 排序，c 无序：

| a   | b   | c   |
| --- | --- | --- |
| 1   | 2   | 3   |
| 1   | 3   | 2   |
| 1   | 4   | 3   |
| 2   | 1   | 3   |
| 2   | 2   | 2   |
| 2   | 3   | 4   |

索引 ca 的组织是先按 c 排序，再按 a 排序，同时记录主键：

| c   | 主键部份a | 主键部份b |
| --- | --------- | --------- |
| 2   | 1         | 3         |
| 2   | 2         | 2         |
| 3   | 1         | 2         |
| 3   | 1         | 4         |
| 3   | 2         | 1         |
| 4   | 2         | 3         |

索引 cb 的组织是先按 c 排序，在按 b 排序，同时记录主键：

| c   | b   | 主键部分a |
| --- | --- | --------- |
| 2   | 2   | 2         |
| 2   | 3   | 1         |
| 3   | 1   | 2         |
| 3   | 2   | 1         |
| 3   | 4   | 1         |
| 4   | 3   | 2         |

```SQL
select * from geek where c=N order by a
```

走ca,cb索引都能定位到满足c=N主键，而且主键的聚簇索引本身就是按order by a,b排序，无序重新排序。所以ca可以去掉

```sql
select * from geek where c=N order by b
```

这条sql如果只有 c单个字段的索引，定位记录可以走索引，但是order by b的顺序与主键顺序不一致，需要额外排序

InnoDB会把主键字段放到索引定义字段后面，
当然同时也会去重。当主键是(a,b)的时候：

- 定义为c的索引，实际上是（c,a,b);
- 定义为(c,a)的索引，实际上是(c,a,b)
- 定义为(c,b）的索引，实际上是（c,b,a)

所以，结论是 ca 可以去掉，cb 需要保留

参考：

- [05 | 深入浅出索引（下）](https://time.geekbang.org/column/article/69636)
- [06 | 全局锁和表锁 ：给表加个字段怎么有这么多阻碍？](https://time.geekbang.org/column/article/69862)
