java String

## 重载"+"与StringBuilder ##

结论： ***对于简单的字符串连接可以让编译器自动优化，也可以使用StringBuilder主动优化。StringBuilder.append()不应该出现字符串连接`+`，在循环中不应该出现字符串连接`+|+=`*** 

结合简单的源码和字节码分析：

反编译命令:`javap -c StringTest`

- java对于使用`+`连接字符串时编译器会使用StringBuilder类来连接优化性能

```java
public static void main(String[] args) {
	String mango = "mango";
	String s = "abc" + mango + "def" + 47;
	System.out.println(s);
}
```
字节码：
```
 public static void main(java.lang.String[]);
    Code:
       0: ldc           #9                  // String mango
       2: astore_1
       3: new           #2                  // class java/lang/StringBuilder
       6: dup
       7: invokespecial #3                  // Method java/lang/StringBuilder."<init>":()V
      10: ldc           #10                 // String abc
      12: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      15: aload_1
      16: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      19: ldc           #11                 // String def
      21: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      24: bipush        47
      26: invokevirtual #12                 // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
      29: invokevirtual #6                  // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
      32: astore_2
      33: getstatic     #7                  // Field java/lang/System.out:Ljava/io/PrintStream;
      36: aload_2
      37: invokevirtual #13                 // Method java/io/PrintStream.println:(Ljava/lang/String;)V
      40: return
}
```
可以看到，源码中并没有使用StringBuilder类，而字节码在code:3中使用new创建了一个StringBuilder对象，并在code:10后使用3次StringBuilder.append()将字符串连接

- 对于简单的字符串连接可以让编译器自动StringBuilder优化，但是如果在循环中使用字符串连接+反而使性能变差

```java
// 在循环中使用字符串连接"+="   不可取
static void implicit(String[] s) {
	String result = "";
	for (int i = 0; i < s.length; i++) {
		result += s[i];
	}
}

// 主动使用StringBuilder并不在append()中使用"+"字符串连接
static void explicit(String[] s) {
	StringBuilder sb = new StringBuilder();
	for (int i = 0; i < s.length; i++) 
		sb.append(s[i]);
}
```
字节码：

```
 static void implicit(java.lang.String[]);
    Code:
       0: ldc           #9                  // String
       2: astore_1
       3: iconst_0
       4: istore_2
       5: iload_2
       6: aload_0
       7: arraylength
       8: if_icmpge     38
      11: new           #2                  // class java/lang/StringBuilder
      14: dup
      15: invokespecial #3                  // Method java/lang/StringBuilder."<init>":()V
      18: aload_1
      19: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      22: aload_0
      23: iload_2
      24: aaload
      25: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      28: invokevirtual #6                  // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
      31: astore_1
      32: iinc          2, 1
      35: goto          5
      38: return



static void explicit(java.lang.String[]);
    Code:
       0: new           #2                  // class java/lang/StringBuilder
       3: dup
       4: invokespecial #3                  // Method java/lang/StringBuilder."<init>":()V
       7: astore_1
       8: iconst_0
       9: istore_2
      10: iload_2
      11: aload_0
      12: arraylength
      13: if_icmpge     30
      16: aload_1
      17: aload_0
      18: iload_2
      19: aaload
      20: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      23: pop
      24: iinc          2, 1
      27: goto          10
      30: return
```
编译器在implicit()的 code:11自动优化使用StringBuilder连接字符串，但是，这个new是在循环内，会不断的创建StringBuilder对象，反而使性能下降。

explicit()没有使用"+"就不会在循环中创建StringBuilder对象，是推荐使用的方式


- 在使用StringBuilder.append()方法时尽量不要使用"+"(特别是在循环中)，编译器仍然会创建新的StringBuilder来连接字符串。

```java
// 在StringBuilder.append()中使用"+"字符串连接  不可取
static void test2(String[] s) {
	StringBuilder sb = new StringBuilder();
	for (int i = 0; i < s.length; i++) 
		sb.append(s[i] + "_" + i);
}
```
字节码:
```
static void test2(java.lang.String[]);
    Code:
       0: new           #2                  // class java/lang/StringBuilder
       3: dup
       4: invokespecial #3                  // Method java/lang/StringBuilder."<init>":()V
       7: astore_1
       8: iconst_0
       9: istore_2
      10: iload_2
      11: aload_0
      12: arraylength
      13: if_icmpge     52
      16: aload_1
      17: new           #2                  // class java/lang/StringBuilder
      20: dup
      21: invokespecial #3                  // Method java/lang/StringBuilder."<init>":()V
      24: aload_0
      25: iload_2
      26: aaload
      27: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      30: ldc           #10                 // String _
      32: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      35: iload_2
      36: invokevirtual #11                 // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
      39: invokevirtual #6                  // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
      42: invokevirtual #4                  // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      45: pop
      46: iinc          2, 1
      49: goto          10
      52: return
```
test2()中主动使用StringBuilder，但是在StringBuilder.append()方法中使用"+"连接字符串，导致编译器在循环中每次创建新的StringBuilder对象(test code:17)，这样主动使用StringBuilder仍然没有提高性能的作用

## 关于String字符串常量池 ##

看了一些答案，涉及到jvm和底层的原理还有c++，暂时来说是没办法研究了，只放一些看的懂的

全局字符串常量池

HotSpot VM里，记录interned string的一个全局表叫做StringTable，它本质上就是个HashSet<String>。这是个纯运行时的结构，而且是惰性（lazy）维护的。注意它只存储对java.lang.String实例的引用，而不存储String对象的内容。 注意，它只存了引用，根据这个引用可以得到具体的String对象。

一个字符串进入了全局的字符串常量池其实是说在这个StringTable中保存了对它的引用，反之，如果说没有在其中就是说StringTable中没有对它的引用。


```java
	public static void main(String[] args) {
		String s1 = new String("he") + new String("llo");
		String s2 = new String("h") + new String("ello");
		String s3 = s1.intern();
		String s4 = s2.intern();
		System.out.println(s1 == s3);// true
		System.out.println(s1 == s4);// true
		System.out.println(s3 == s4);// true
	}
```

类加载阶段，什么都没干。

然后运行main方法

先看第一句，会创建"he"和"llo"对象，并放入字符串常量池，然后会创建一个"hello"对象，没有放入字符串常量池，s1指向这个"hello"对象。

第二句，创建"h"和"ello"对象，并放入字符串常量池，然后会创建一个"hello"对象，没有放入字符串常量池，s2指向这个"hello"对象。

第三句，字符串常量池里面还没有，于是会把s1指向的String对象的引用放入字符串常量池（换句话说，放入池中的引用和s1指向了同一个对象），然后会把这个引用返回给了s3，所以s3==s1是true。

第四句，字符串常量池里面已经有了，直接将它返回给了s4，所以s4==s1是true。

原文链接：[https://www.zhihu.com/question/55994121](https://www.zhihu.com/question/55994121 "Java 中new String(\"字面量\") 中 "字面量" 是何时进入字符串常量池的?")


贴个jvm的string相关链接:[http://rednaxelafx.iteye.com/blog/774673](http://rednaxelafx.iteye.com/blog/774673 "请别再拿“String s = new String(\"xyz\")创建了多少个String实例”来面试了吧")

## StringBuilder的使用和分析 ##

### 清空StringBuilder ###

stringbuilder并没有直接提供clear()这样的api

从网上的资料来看，有三种清空方式
- stringbuilder.setLength()
- stringbuilder.delete()
- new StringBuilder()

new的方式不在考虑范围内

***结论：*** 对于delete(0, sb.length())和setLength(0)，两者几乎没有差别，应该**选择更简洁的`setLength()`**

对比前两种方式，下面是结合stringbuilder和其超类AbstractStringBuilder的源码分析

stringbuilder.delete()源码

```java
    /**
       StringBuilder调用超类AbstractStringBuilder.delete方法
    */
    @Override
    public StringBuilder delete(int start, int end) {
        super.delete(start, end);
        return this;
    }

    public AbstractStringBuilder delete(int start, int end) {
        if (start < 0)
            throw new StringIndexOutOfBoundsException(start);
        if (end > count)
            end = count;
        if (start > end)
            throw new StringIndexOutOfBoundsException();
        int len = end - start;
        if (len > 0) {
            System.arraycopy(value, start+len, value, start, count-end);
            count -= len;
        }
        return this;
    }
```
stringbuilder.setLength()源码

```java
    /**
    设置stringbuilder字符序列长度为newLength，对于在newLength范围内原来的下标index的字符不会改变，
    之前范围内可能不存在的字符将置为null,之前范围外可能存在的字符置为null。newLength必须>= 0
    */
    public void setLength(int newLength) {
        if (newLength < 0)
            throw new StringIndexOutOfBoundsException(newLength);
        ensureCapacityInternal(newLength);

        if (count < newLength) {// 设置范围内不存在的字符为null(ascii中的"\0"表示null)
            Arrays.fill(value, count, newLength, '\0');
        }

        count = newLength;
    }

    private void ensureCapacityInternal(int minimumCapacity) {
        // overflow-conscious code
        if (minimumCapacity - value.length > 0) {
            value = Arrays.copyOf(value,
                    newCapacity(minimumCapacity));
        }
    }
```

在delete中看似存在数组的复制System.arraycopy()，但是当delete(0, sb.length())时，count-end=0，不会真正的复制数组，而是直接count -= len;

同样setLength(0)执行 count = newLength，和delete是一样的效果






