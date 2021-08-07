# mybatis generator使用mysql生成时使用多个库问题

在使用mybatis generator连接mysql生成代码时，其它库中的表数据会被生成entity,xml,mapper，jdbc url中指定了数据库`jdbc:mysql://localhost:33060/user_center`，但是在generator中读取到了其它包括系统数据库

```bash
23:09:50.550 [main] DEBUG org.mybatis.generator.logging.LogFactory - Logging initialized using 'org.mybatis.generator.logging.slf4j.Slf4jLoggingLogFactory@156b88f5' adapter.
#...
23:09:50.778 [main] DEBUG org.mybatis.generator.internal.db.DatabaseIntrospector - Found column "audit_status", data type 12, in table "content_center..share_info"
23:09:50.778 [main] DEBUG org.mybatis.generator.internal.db.DatabaseIntrospector - Found column "reason", data type 12, in table "content_center..share_info"
#...
23:09:50.779 [main] DEBUG org.mybatis.generator.internal.db.DatabaseIntrospector - Found column "USER", data type 12, in table "information_schema..ADMINISTRABLE_ROLE_AUTHORIZATIONS"
# ...
23:09:50.785 [main] DEBUG org.mybatis.generator.internal.db.DatabaseIntrospector - Found column "GRANTEE_HOST", data type 12, in table "information_schema..APPLICABLE_ROLES"
23:09:50.785 [main] DEBUG org.mybatis.generator.internal.db.DatabaseIntrospector - Found column "ROLE_NAME", data type 12, in table "information_schema..APPLICABLE_ROLES"
#...
Column id, specified as an identity column in table events_statements_histogram_by_digest, does not exist in the table.
Column id, specified as an identity column in table waits_global_by_latency, does not exist in the table.
Column id, specified as an identity column in table slow_log, does not exist in the table.
Column id, specified as an identity column in table x$wait_classes_global_by_avg_latency, does not exist in the table.
Column id, specified as an identity column in table slave_master_info, does not exist in the table.
```

环境：

- `mysql  Ver 8.0.21 for Linux on x86_64 (MySQL Community Server - GPL)`
- java 11

```xml
<dependency>
    <groupId>org.mybatis.generator</groupId>
    <artifactId>mybatis-generator-core</artifactId>
    <version>1.4.0</version>
</dependency>
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.21</version>
</dependency>
```

generatorConfig.xml部分配置

```xml
<jdbcConnection driverClass="${db.driverClass}"
                connectionURL="${db.url}"
                userId="${db.username}"
                password="${db.password}">
</jdbcConnection>
        <table tableName="%" >
    <generatedKey column="id" sqlStatement="MySQL" identity="true" />
</table>
```

## 解决方法

解决方法非常简单，只需将jdbcConnection的nullCatalogMeansCurrent属性设置为true即可

```xml
<context id="mysql-user-center" targetRuntime="MyBatis3" defaultModelType="flat">
    <!-- ... -->
    <jdbcConnection driverClass="${db.driverClass}"
                    connectionURL="${db.url}"
                    userId="${db.username}"
                    password="${db.password}">
        <property name="nullCatalogMeansCurrent" value="true" />
    </jdbcConnection>
    <!-- ... -->
</context>
```

参考：

- [解决mybatis generator使用新版mysql驱动8.0版本时会生成用户下多个库里的表的问题](https://blog.csdn.net/gnail_oug/article/details/84785850)
- [MySql Usage Notes](http://mybatis.org/generator/usage/mysql.html)
