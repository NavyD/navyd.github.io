# Mybatis Generator自定义type resolver

## 描述

在使用MBG时，mysql中的is前缀的列转换为Byte类型，与需求使用Boolean不符合

版本信息：`mysql 8.0.21, jdbc mysql cj: 8.0.21`

```sql
CREATE TABLE `share_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'id',
  #...
  `is_original` tinyint unsigned NOT NULL COMMENT '是否原创 0:否 1:是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='分享表'
```

```java
public class ShareInfo extends BaseEntity implements Serializable {
    /**
     * 是否原创 0:否 1:是
     *
     * @mbg.generated
     */
    private Byte original;
    //...
}
```

## 原因

MBG配置通过`javaTypeResolver`标签解析，对应`org.mybatis.generator.api.JavaTypeResolver`接口与实现`JavaTypeResolverDefaultImpl`。

`JavaTypeResolverDefaultImpl`在构造器中对jdbc与java type做了type mapping：

```java
public JavaTypeResolverDefaultImpl() {
    super();
    properties = new Properties();
    typeMap = new HashMap<>();
    // bit to boolean
    typeMap.put(Types.BIT, new JdbcTypeInformation("BIT", //$NON-NLS-1$
            new FullyQualifiedJavaType(Boolean.class.getName())));
    // ...  
    // tinyint to byte
    typeMap.put(Types.TINYINT, new JdbcTypeInformation("TINYINT", //$NON-NLS-1$
            new FullyQualifiedJavaType(Byte.class.getName())));
    // ...
}
```

在`calculateJavaType`方法中计算jdbc对应java type，使用默认type mapping和可能覆盖的`overrideDefaultType`

```java
public FullyQualifiedJavaType calculateJavaType(
        IntrospectedColumn introspectedColumn) { // column: is_original
    // ...
    JdbcTypeInformation jdbcTypeInformation = typeMap
            .get(introspectedColumn.getJdbcType());// jdbcType: TINYINT

    if (jdbcTypeInformation != null) {
        answer = jdbcTypeInformation.getFullyQualifiedJavaType(); // Byte
        answer = overrideDefaultType(introspectedColumn, answer); // Byte
    }
    // ...
}
```

jdbc解析为column is_original为tinyint类型，导致sql column `share_info.is_original`进来时作为Byte处理

***注意*** ：由`DatabaseIntrospector`解析jdbc ResultSet创建`introspectedColumn`。如果column定义是`is_original tinyint(1) not null`，则会被jdbc解析为`BIT`类型，通过type mapping对应到java type: Boolean

至此，知道了是对列`TINYINT`解析的问题。

不能直接对所有tinyint转boolean，可尝试用`tinyint(1)`列定义转换为boolean类型。修改列定义并查看是否有效

```sql
alter table share_info modify column is_original tinyint(1) unsigned NOT NULL COMMENT '是否原创 0:否 1:是';
# Query OK, 2 rows affected
show create table share_info\G
/*
***************************[ 1. row ]***************************
Table        | share_info
Create Table | CREATE TABLE `share_info` (
#...
  `is_original` tinyint unsigned NOT NULL COMMENT '是否原创 0:否 1:是',
#...
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='分享表'
*/
```

可以看到并没有生效，在MBG debug发现`introspectedColumn.length==3`，而不是当`is_original tinyint(1) NOT NULL`时`length==1`，这应该是mysql 8.x的坑

转换思路，可以只转换`is_`前缀的列到`Boolean`就行，不需要修改列定义，这样还更精确

## 解决方案

通过column name转换`is_`前缀的列到`Boolean`，并在MBG配置文件中配置`javaTypeResolver`

```java
public class MyJavaTypeResolver extends JavaTypeResolverDefaultImpl {
    private static final String BOOLEAN_PREFIX = "is_";
    @Override
    public FullyQualifiedJavaType calculateJavaType(IntrospectedColumn introspectedColumn) {
        if (introspectedColumn.getActualColumnName().startsWith(BOOLEAN_PREFIX)) {
            return new FullyQualifiedJavaType(Boolean.class.getName());
        } else {
            return super.calculateJavaType(introspectedColumn);
        }
    }
}
```

```xml
<javaTypeResolver type="xyz.navyd.mbg.MyJavaTypeResolver">
    <property name="forceBigDecimals" value="false" />
    <property name="useJSR310Types" value="true" />
</javaTypeResolver>
```
