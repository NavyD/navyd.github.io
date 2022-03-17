---
title: "Sql Driver and Spi"
date: 2022-03-18T01:09:41+08:00
draft: true
---

java.sql.Driver是如何加载的

<!--more-->

## 分析

因为数据库驱动类的特殊性质，JDBC 规范中明确要求 Driver 类必须向 DriverManager 注册自己，导致其必须由 class.forName 手动触发。

在最新的DriverManager文档中提到使用两种方式加载driver

* system property:vm启动-Dpropertyname=value或System.setProperty(key,val)设置
* 使用service-provider loading mechanism SPI机制

## SPI

在`mysql-connector-java-8.0.xx.jar`中存在文件`META-INF\services\java.sql.Driver`一行内容：

```
com.mysql.cj.jdbc.Driver
```

使用`java.util.ServiceLoader`调用主类无需变更代码，这符合开闭原则。只要classpath中存在这样的文件，就可以自动加载接口实现

下面是`java.sql.DriverManager#ensureDriversInitialized()`部分源码：

```java

            String drivers;
            try {
                drivers = AccessController.doPrivileged(new PrivilegedAction<String>() {
                    public String run() {
                        return System.getProperty(JDBC_DRIVERS_PROPERTY);
                    }
                });
            } catch (Exception ex) {
                drivers = null;
            }
            // If the driver is packaged as a Service Provider, load it.
            // Get all the drivers through the classloader
            // exposed as a java.sql.Driver.class service.
            // ServiceLoader.load() replaces the sun.misc.Providers()

            AccessController.doPrivileged(new PrivilegedAction<Void>() {
                public Void run() {

                    ServiceLoader<Driver> loadedDrivers = ServiceLoader.load(Driver.class);
                    Iterator<Driver> driversIterator = loadedDrivers.iterator();

                    /* Load these drivers, so that they can be instantiated.
                     * It may be the case that the driver class may not be there
                     * i.e. there may be a packaged driver with the service class
                     * as implementation of java.sql.Driver but the actual class
                     * may be missing. In that case a java.util.ServiceConfigurationError
                     * will be thrown at runtime by the VM trying to locate
                     * and load the service.
                     *
                     * Adding a try catch block to catch those runtime errors
                     * if driver not available in classpath but it's
                     * packaged as service and that service is there in classpath.
                     */
                    try {
                        while (driversIterator.hasNext()) {
                            driversIterator.next();
                        }
                    } catch (Throwable t) {
                        // Do nothing
                    }
                    return null;
                }
            });
```

参考：

* [Introduction to the Service Provider Interfaces](https://docs.oracle.com/javase/tutorial/sound/SPI-intro.html)
* [class ServiceLoader](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/ServiceLoader.html)
* [JAVA 拾遗 —— 关于 SPI 机制](https://www.iocoder.cn/Fight/xuma/spi/?self)
