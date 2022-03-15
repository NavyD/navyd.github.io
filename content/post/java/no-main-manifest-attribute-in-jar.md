---
title: "No Main Manifest Attribute in XXX.Jar"
date: 2022-03-15T23:30:06+08:00
draft: false
tags: [java, jar, maven, package]
---

在使用maven直接构建的jar包无法被java执行：

```sh
$ java -jar target/hello-maven-0.0.1.jar
no main manifest attribute, in target/hello-maven-0.0.1.jar
```

<!--more-->

下面是pom.xml与java文件

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>xyz.navyd</groupId>
    <artifactId>hello-maven</artifactId>
    <version>0.0.1</version>
    <name>test</name>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.10.1</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

```java
package xyz.navyd.hello_maven;

public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("hello world maven!");
    }
}
```

## 分析

在pom.xml中没有配置打包的plugin，maven默认使用[Apache Maven Archiver](https://maven.apache.org/shared/maven-archiver/index.html)打包，可以在target中看到maven-archiver的配置

```sh
$ tree -L 2 target
target
├── classes
│  └── xyz
├── generated-sources
│  └── annotations
├── generated-test-sources
│  └── test-annotations
├── maven-archiver
│  └── pom.properties
├── maven-status
│  └── maven-compiler-plugin
├── test-classes
└── hello-maven-0.0.1.jar
```

通过Maven Archiver打包的默认Manifest

```
Manifest-Version: 1.0
Created-By: Apache Maven ${maven.version}
Build-Jdk: ${java.version}
```

jar包文件

```sh
# 过滤size=0的文件夹
$ unzip -l target/hello-maven-0.0.1.jar | grep -vE '^\s+0'
Archive:  target/hello-maven-0.0.1.jar
  Length      Date    Time    Name
---------  ---------- -----   ----
      129  2022-03-15 22:36   META-INF/MANIFEST.MF
      584  2022-03-15 22:36   xyz/navyd/hello_maven/HelloWorld.class
      836  2022-03-15 22:36   META-INF/maven/xyz.navyd/hello-maven/pom.xml
      105  2022-03-15 22:36   META-INF/maven/xyz.navyd/hello-maven/pom.properties
---------                     -------
     1654                     11 files
```

下面是打包后jar中的MANIFEST.MF文件内容

```
Manifest-Version: 1.0
Archiver-Version: Plexus Archiver
Created-By: Apache Maven 3.8.4
Built-By: navyd
Build-Jdk: 11.0.14


```

在[jar规范](https://docs.oracle.com/en/java/javase/17/docs/specs/jar/jar.html#main-attributes)中提到可运行的jar包必要Main-Class属性，也就是说需要调整打包配置Manifest

## 解决

[How to Create an Executable JAR with Maven](https://www.baeldung.com/executable-jar-with-maven)

参考：

* [JAR Manifest](https://docs.oracle.com/en/java/javase/17/docs/specs/jar/jar.html#jar-manifest)
* [Apache Maven JAR Plugin](https://maven.apache.org/plugins/maven-jar-plugin/index.html)
* [Apache Maven Archiver/Manifest](https://maven.apache.org/shared/maven-archiver/examples/manifest.html)
* [How to Create an Executable JAR with Maven](https://www.baeldung.com/executable-jar-with-maven)
