# 文件写入与Base64解码错误

记录一次在写入文件后取出再次解码base64时出现IllegalArgumentException:`Input byte array has incorrect ending byte at 92364`

```java
java.lang.IllegalArgumentException: Input byte array has incorrect ending byte at 92364
        at java.base/java.util.Base64$Decoder.decode0(Base64.java:819) ~[na:na]
        at java.base/java.util.Base64$Decoder.decode(Base64.java:567) ~[na:na]
        at java.base/java.util.Base64$Decoder.decode(Base64.java:590) ~[na:na]
        at xyz.navyd.util.V2rayUtils.parseV2rayNodesToBytes(V2rayUtils.java:207) ~[classes!/:0.1.0]
```

## 分析

文件是直接在将base64编码的byte直接写入，取出时直接base64解码，没有任何中间转换。在debug时发现在`92364`后面确实存在一段：`=Z01TNDFlQ0I4SUU1R0lFSkNReUJEYUdGdU5DSXNJbkpsYldGeWF5...`。但这不是特殊字符，而且之前直接保存文件是可以正常取出解码的，说明不是编码的问题。又使用正常的内存读写，避免使用文件读写，真是找出问题了，在同一时间下，在内存中debug时base64编码的`byte[]`长度length=92364，但是之前在文件debug时长度是`95000`，明显是文件写入的问题，多出来未知的字节。

重新检查文件写入的代码：

```java
try (var fc = FileChannel.open(path, StandardOpenOption.WRITE, StandardOpenOption.CREATE)) {
    var buf = ByteBuffer.wrap(bytes);
    var len = 0;
    while (buf.hasRemaining()) {
        fc.write(buf);
    }
    fc.force(true);
} // ...
```

可以看到FileChannel使用的文件打开属性：`WRITE,CREATE`都没有提到对已存在的文件内容如何处理的，FileChannel的文档中提到是`The size of the file increases when bytes are written beyond its current size; the size of the file decreases when it is truncated.`，而我的需求是不停的更新文件内容，不要保持之前的内容。也就是说，如果当前写入的内容不如之前的文件内容多，则写入时后面的内容会同时保留，这就是为何出现文件长度会比在内存的长度大

多说一句，base64不是可读的，但是可以使用vscode base64 de/encode插件直接转换，但是对不合法的地方没有错误提示，来回检查了好几次都是正常的，java这边又不停的出错，google又没有类似的问题，什么`trim`去除多余字符没用，windows -> linux编码也没有。还是debug靠谱

## 解决

有两种方式：

* StandardOpenOption中提供了一个option`TRUNCATE_EXISTING`:`If the file already exists and it is opened for WRITE access, then its length is truncated to 0.`直接使用即可

```java
try (var fc = FileChannel.open(path, WRITE, CREATE, TRUNCATE_EXISTING)) {
    var buf = ByteBuffer.wrap(bytes);
    var len = 0;
    while (buf.hasRemaining()) {
        fc.write(buf);
    }
    fc.force(true);
} // ...
```

* 使用`fc.truncate(0);`主动清空文件

```java
try (var fc = FileChannel.open(path, StandardOpenOption.WRITE, StandardOpenOption.CREATE)) {
    fc.truncate(0);
    var buf = ByteBuffer.wrap(bytes);
    var len = 0;
    while (buf.hasRemaining()) {
        fc.write(buf);
    }
    fc.force(true);
} // ...
```
