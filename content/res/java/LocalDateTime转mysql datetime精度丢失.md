# LocalDateTime转mysql datetime精度丢失

## 现象

在测试插入gmtCreate, gmtModified比较java中`LocalDateTime.now()`的 ***纳秒*** 插入到mysql datetime，取出后的LocalDateTime只精确到秒

```sql
drop table if exists product_category;
create table product_category(
    id int unsigned not null auto_increment,
    category_name varchar(64) not null,
    gmt_create datetime not null default current_timestamp,
    gmt_modified datetime not null default current_timestamp on update current_timestamp,
    primary key(id)
);
```

在网上找到[使用LocalDateTime遇到的问题](https://www.jianshu.com/p/634a41503f42)，可能是mysql datetime入库时根据纳秒进行四舍五入

```java
void insertGmtTime() {
    var insertObj = getNewObjects().get(0);
    var mapper = getBaseMapper();
    assertThat(mapper.insert(insertObj)).isEqualTo(1);

    assertThat(mapper.selectById(insertObj.getId()))
            .isNotNull()
            // withNano 舍去纳秒
            .matches(o -> o.getGmtCreate().equals(insertObj.getGmtCreate().withNano(0))
                    && o.getGmtModified().equals(insertObj.getGmtModified().withNano(0)),
                    "insert obj: " + insertObj
            );
}
```

在去除纳秒后出现四舍五入导致的秒进位不等错误：

java now: `gmtCreate=2020-08-09T19:11:29.708034400, gmtModified=2020-08-09T19:11:29.708034400`

mysql datetime: `gmtCreate=2020-08-09T19:11:30, gmtModified=2020-08-09T19:11:30`

```
java.lang.AssertionError: 
Expecting:
  <ProductCategory(super=BaseEntity(id=3, gmtCreate=2020-08-09T19:11:30, gmtModified=2020-08-09T19:11:30), categoryName=新分类_101)>
to match 'insert obj: ProductCategory(super=BaseEntity(id=3, gmtCreate=2020-08-09T19:11:29.708034400, gmtModified=2020-08-09T19:11:29.708034400), categoryName=新分类_101)' predicate.
```

## 原因

开始以为是mybatis转换的问题，[Mybatis源代码分析之类型转换](https://www.cnblogs.com/sunzhenchao/archive/2013/04/09/3009431.html)中注意有`org.apache.ibatis.type.LocalDateTimeTypeHandler`，这个类可转换LocalDateTime与jdbc type ？？

发现直接用jdbc处理，这样问题就可能出现在mysql中了

对`product_category`插入记录时间`2020-08-09T19:11:29.708034400`，结果`2020-08-09 19:11:30`还是只到秒，纳秒丢失：

```sql
insert into product_category(category_name, gmt_create) values('test', '2020-08-09T19:11:29.708034400');
select * from product_category;
-- test	2020-08-09 19:11:30	2020-08-09 20:01:41
```

调查后发现，如果创建表示字段类型为datetime或者timestamp时，默认精度是到秒的，也就是说如果想保存毫秒的精度，需要主动指定精度`datetime(6)`，最大到6

```sql
drop table if exists product_category;
create table product_category(
    id int unsigned not null auto_increment,
    category_name varchar(64) not null,
    gmt_create datetime(2) not null,
    gmt_modified datetime(6) not null,
    primary key(id)
);
insert into product_category(category_name, gmt_create, gmt_modified) values('test', '2020-08-09T19:11:29.708034400', '2020-08-09T19:11:29.708034400');
SELECT * FROM sell.product_category;
-- category_name    gmt_create  gmt_modified
-- test	2020-08-09 19:11:29.71	2020-08-09 19:11:29.708034
```

参考：[mysql8.0.11 datetime精度丢失的问题](https://blog.csdn.net/sinat_29899265/article/details/91990485)

## 方法

- 统一java LocalDateTime和 mysql datetime精度- 

插入时精度为秒不会有四舍五入：`LocalDateTime.withNano(0)`

```java
    void insertGmtTime() {
        var insertObj = getNewObjects().get(0);
        insertObj.setGmtCreate(insertObj.getGmtCreate().withNano(0));
        insertObj.setGmtModified(insertObj.getGmtModified().withNano(0));
        var mapper = getBaseMapper();
        assertThat(mapper.insert(insertObj)).isEqualTo(1);
        assertThat(mapper.selectById(insertObj.getId()))
                .isNotNull()
                .matches(o -> o.getGmtCreate().equals(insertObj.getGmtCreate())
                        && o.getGmtModified().equals(insertObj.getGmtModified()),
                        "insert obj: " + insertObj
                );
    }
```

参考：[LocalDateTime在项目中的使用（LocalDateTime对接前端通过时间戳互转、LocalDateTime对接数据库）](https://www.yht7.com/news/61725)
