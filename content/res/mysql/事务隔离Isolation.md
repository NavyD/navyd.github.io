# 事务隔离Isolation

## 配置隔离级别

参考：[13.3.7 SET TRANSACTION Statement](https://dev.mysql.com/doc/refman/8.0/en/set-transaction.html)

[[不同隔离级别的事务间有何影响.md]]

### Transaction Isolation Levels

- `REPEATABLE READ`
- `READ COMMITTED`
- `READ UNCOMMITTED`
- `SERIALIZABLE`

### Transaction Access Mode

- `READ WRITE`
- `READ ONLY`

### Transaction Characteristic Scope

| Syntax                                             | Affected Characteristic Scope |
| -------------------------------------------------- | ----------------------------- |
| SET GLOBAL TRANSACTION transaction_characteristic  | Global                        |
| SET SESSION TRANSACTION transaction_characteristic | Session                       |
| SET TRANSACTION transaction_characteristic         | Next transaction only         |

如果没有在事务中语句中声明scope，如：`SET TRANSACTION ISOLATION LEVEL SERIALIZABLE`则

- 仅对下次事务使用且只应用一次，后续事务使用当前session level

	```SQL
	select @@transaction_isolation; # REPEATABLE-READ   
	select @@transaction_read_only; # 0
	# 设置Next transaction only
	set transaction isolation level READ COMMITTED, read only; # ok
	# next transaction
	start transaction;
	# 无法查看 Next transaction only
	select @@transaction_isolation; # REPEATABLE-READ
	select @@transaction_read_only; # 0
	# Next transaction only确实生效
	update t set k=k+1 where id=1; 	# (1792, 'Cannot execute statement in a READ ONLY transaction.');
	rollback;
	# next next transaction
	start transaction
	select @@transaction_read_only 	# 0
	# 使用session REPEATABLE-READ 
 	update t set k=k+1 where id=1;	# Query OK, 1 row affected
	commit; # ok
	```

- 不允许在事务中改变级别

	```SQL
	START TRANSACTION;
	# (1568, "Transaction characteristics can't be changed while a transaction is in progress")
	SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
	```

### 查看事务隔离级别

```SQL
# 全局
select @@global.transaction_isolation
# REPEATABLE-READ

# 当前session
select @@transaction_isolation;
#  REPEATABLE-READ
```

`Next transaction level` `Current transaction level`没有方式可以查询

参考：[Mysql - How to find out isolation level for the transactions](https://stackoverflow.com/a/50941611/8566831)

### 如何配置

```sql
# 修改全局事务隔离级别
set global transaction isolation level READ COMMITTED, READ WRITE;

# 修改当前会话的事务隔离级别
set session transaction isolation level READ COMMITTED, READ WRITE;
```

server启动时全局配置文件参数：

```ini
[mysqld]
transaction-isolation = REPEATABLE-READ
transaction-read-only = OFF
```

## 隔离级别与解决的问题

| ISOLATION        | DIRTY READ | NON-REPEATABLE READ | PHANTOM READ |
| ---------------- | ---------- | ------------------- | ------------ |
| READ-UNCOMMITTED | YES        | YES                 | YES          |
| READ-COMMITTED   | NO         | YES                 | YES          |
| REPEATABLE-READ  | NO         | NO                  | YES or NO    |
| SERIALIZABLE     | NO         | NO                  | NO           |

### 并发问题

下面使用这个表进行测试

```SQL
CREATE TABLE `t` (
  `id` int NOT NULL,
  `k` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
insert into t values(1,1);
```

| id  | k   |
| --- | --- |
| 1   | 1   |

#### DIRTY READ

事务读期间未提交的脏数据可见

| step | session A                                                  | session B                                                  |
| ---- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| 1    | `set session transaction isolation level READ UNCOMMITTED` | `set session transaction isolation level READ UNCOMMITTED` |
| 2    | start transaction;                                         | start transaction;                                         |
| 3    | select * from t; #(1,1)                                    |                                                            |
| 4    |                                                            | update t set k=k+1 where id=1; #(1,2)                      |
| 5    | select * from t; #(1,2)                                    |                                                            |
| 6    |                                                            | rollback;                                                  |
| 7    | select * from t; #(1,1)                                    |                                                            |
| 8    | commit;                                                    |                                                            |

在session B update前后rollback，session A 3次查询的结果都不同：`k=1,k=2,k=1`，***存在脏读问题***

#### NON-REPEATABLE READ

事务提交前后行重复读列值不同

| step | session A                                                | session B                                                |
| ---- | -------------------------------------------------------- | -------------------------------------------------------- |
| 1    | `set session transaction isolation level READ COMMITTED` | `set session transaction isolation level READ COMMITTED` |
| 2    | start transaction;                                       | start transaction;                                       |
| 3    | select * from t; #(1,1)                                  |                                                          |
| 4    |                                                          | update t set k=k+1 where id=1; #(1,2)                    |
| 5    | select * from t; #(1,1)                                  |                                                          |
| 6    |                                                          | commit;                                                  |
| 7    | select * from t; #(1,2)                                  |                                                          |
| 8    | commit;                                                  |                                                          |

session B提交前session A不能查询到B已经更新的数据，***使用READ COMMITTED解决了脏读问题***

session B提交后session A查询结果与上一步不一致，***使用READ COMMITTED存在不可重复读的问题***

#### PHANTOM READ

行的范围多次读不同 增多/减少

| step | session A                                                 | session B                                                 |
| ---- | --------------------------------------------------------- | --------------------------------------------------------- |
| 1    | `set session transaction isolation level REPEATABLE READ` | `set session transaction isolation level REPEATABLE READ` |
| 2    | start transaction;                                        | start transaction;                                        |
| 3    | select * from t; #(1,1)                                   |                                                           |
| 4    |                                                           | insert into t values(2, 2); #(1,1), (2,2)                 |
| 5    |                                                           | commit;                                                   |
| 6    | select * from t; #(1,1)                                   |                                                           |
| 7    | select * from t for update; #(1,1), (2,2)                 |                                                           |
| 8    | insert into t values(2,2); # error: 1062 Duplicate entry  |                                                           |
| 9    | commit;                                                   |

可以看到在session B插入数据提交后session A *快照读* `select`都不能看到B的更新，没有出现幻读

当session A使用*当前读* `select...for update`时，可以看到多出一行，且在A insert id=2时出现Duplicate entry的错误，*出现了幻读*

如果session B不是插入一行，而是修改k值：

| step | session A                                                   | session B                                                 |
| ---- | ----------------------------------------------------------- | --------------------------------------------------------- |
| 1    | `set session transaction isolation level REPEATABLE READ`   | `set session transaction isolation level REPEATABLE READ` |
| 2    | start transaction;                                          | start transaction;                                        |
| 3    | select * from t; #(1,1),(2,2)                               |                                                           |
| 4    |                                                             | update t set k = 3 where id=1; #(1,3), (2,2)              |
| 5    |                                                             | commit;                                                   |
| 6    | select * from t; #(1,1),(2,2)                               |                                                           |
| 7    | update t set k = 5 where k = 1; # Query OK, 0 rows affected |                                                           |
| 8    | select * from t for update; #(1,3),(2,2)                    |                                                           |
| 9    | commit;                                                     |

可以看到，虽然在B提交后，A update提示Query OK，但更新行数为0，很明显与快照读select不符合，出现了幻读。

参考：

- [MySQL 事务隔离级别解析和实战](https://juejin.im/post/6844903796099776519)
- [一文讲清楚MySQL事务隔离级别和实现原理，开发人员必备知识点](https://www.cnblogs.com/fengzheng/p/12557762.html)

[[如何解决幻读.md]]

## 事务隔离的实现

Isolation实现涉及多个方面，暂时不能找全，现在仅从MVCC讨论

### MVCC

[[MVCC.md]]

### 锁

### 时间戳

## 参考

- [『浅入深出』MySQL 中事务的实现](https://draveness.me/mysql-transaction/)

--------------------------------

#### 可见性异常

##### 定义

能看到当前事务不存在的状态

##### 原因

- MVCC一致性视图
- select当前读

### 隔离级别

#### READ UNCOMMITTED

#### READ COMMITTED

- dirty read

#### REPEATABLE READ

- non-repeatable read
- phantom read

- 快照读不会出现？
- 当前读可出现幻读

#### SERIALIZABLE

同行记录读写锁

### 更新提交前后在事务不同的隔离级别的区别

	- RU

		- 前后可见

	- RC

		- 后可见

	- RR

		- 前后不可见

- 一致性读Consistent Read

	- 定义

		- 使用MVCC提供在某个时间点上的query snapshot

	- 快照读snapshot

		- 定义

			- 某个时间点的数据形式

		- MVCC实现

	- read view

		- 组成

			- 事务活跃数组arr

				- min=未提交的最小id
				- max=当前事务id（最大创建id）

		- 可见性规则如何判断

			- 可见

				- row trx_id < arr min
				- trx_id <= arr max && not in arr

			- 不可见

				- row trx_id > arr max
				- trx_id < arr max && in arr

		- 何时创建

			- RC：每个SQL语句
			- RR：事务创建后首读SQL

- 当前读current read

	- 定义

		- 更新先读后写

	- 触发方式

		- update
		- select ... for update/lock in share mode

	- 两个事务更新同一行当前读如何处理

		- 两阶段锁协议

	- RR出现幻读？

### 定义

- 一组操作都成功或失败

## 操作

### 启动方式

- set autocommit=0
- begin/start transaction
- commit work and chain

- start transaction with consistent snapshot 

### 配置

- 隔离级别

	- 启动参数 transaction-isolation

### 长事务

- 如何查询

  ```sql
  select * from information_schema.innodb_trx where TIME_TO_SEC(timediff(now(),trx_started))>60
  ```

	- information_schema.innodb_trx.trx_started

- 影响

	- undo log保留过大

		- mysql5.5<=回滚段不变小

			- 重建

	- 锁资源占用

- 如何避免

	- 应用端步骤

		- set autocommit=1
		- 去掉不必要的只读事务
		- SET MAX_EXECUTION_TIME 限制语句执行时间

	- 数据库步骤

		- 长事务kill or 报警
		- 分析日志
		- innodb_undo_tablespaces >= 2

## 问题

### 并发减库存出现<0

- 原因

	- 先一致性读后当前读update

- 解决方式

	- select...for update
	- update ... where total_quan >= quan, affected_rows == 1

### update: affected_rows=0, rows matched=0

- 原因

	- update前被其它事务update where中的列值

## 实现

### MVCC

- 作用

	- 实现了 RC RR隔离级别的事务执行Consistent Read
	- 提高并发

- undo log

	- 记录修改
	- 回滚
	- 何时删除

		- 没有任何事务视图需要 undo log

- 如何获取事务的数据版本

	- 行记录当前读
	- transaction id
	- undo log计算

		- 如何工作

- 结构

	- 隐藏列

		- create time
		- version number

