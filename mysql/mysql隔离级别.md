# mysql隔离级别

## 问题

### 幻读

| session 1              | session 2                            |
| ---------------------- | ------------------------------------ |
| begin                  | begin                                |
| SELECT * FROM t_bitfly |
|                        | INSERT INTO t_bitfly VALUES (1, 'a') |
