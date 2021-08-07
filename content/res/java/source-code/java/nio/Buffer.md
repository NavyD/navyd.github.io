Buffer

缓冲区基础

什么是缓冲区？
Buffer 是一个对象， 它包含一些要写入或者刚读出的数据。 在 NIO 中加入 Buffer 对象，体现了新库与原 I/O 的一个重要区别。在面向流的 I/O 中，您将数据直接写入或者将数据直接读到 Stream 对象中。

在 NIO 库中，**所有数据都是用缓冲区处理的**。在读取数据时，它是直接读到缓冲区中的。在写入数据时，它是写入到缓冲区中的。任何时候访问 NIO 中的数据，您都是将它放到缓冲区中。

**缓冲区实质上是一个数组**。通常它是一个字节数组，但是也可以使用其他种类的数组。但是一个缓冲区不 仅仅 是一个数组。缓冲区提供了对数据的结构化访问，而且还可以跟踪系统的读/写进程。




通道类型

通道与流的不同之处在于**通道是双向的**。而流只是在一个方向上移动(一个流必须是 InputStream 或者 OutputStream 的子类)， 而 **通道 可以用于读、写或者同时用于读写。**
因为它们是双向的，所以通道可以比流更好地反映底层操作系统的真实情况。特别是在 UNIX 模型中，底层操作系统通道是双向的。

从理论到实践：NIO 中的读和写

概述

读和写是 I/O 的基本过程。从一个通道中读取很简单：只需创建一个缓冲区，然后让通道将数据读到这个缓冲区中。写入也相当简单：创建一个缓冲区，用数据填充它，然后让通道用这些数据来执行写入操作。

在本节中，我们将学习有关在 Java 程序中读取和写入数据的一些知识。我们将回顾 NIO 的主要组件(缓冲区、通道和一些相关的方法)，看看它们是如何交互以进行读写的。在接下来的几节中，我们将更详细地分析这其中的每个组件以及其交互。

从文件中读取

在我们第一个练习中，我们将从一个文件中读取一些数据。如果使用原来的 I/O，那么我们只需创建一个 FileInputStream 并从它那里读取。而在 NIO 中，情况稍有不同：

我们首先从 FileInputStream 获取一个 Channel 对象，然后使用这个通道来读取数据。

在 NIO 系统中，任何时候执行一个读操作，您都是从通道中读取，但是您不是 直接 从通道读取。因为所有数据最终都驻留在缓冲区中，所以您是从通道读到缓冲区中。

因此读取文件涉及三个步骤：

- (1) 从 FileInputStream 获取 Channel，
- (2) 创建 Buffer，
- (3) 将数据从 Channel 读到 Buffer 中。

现在，让我们看一下这个过程。

读取文件

    FileInputStream fin = new FileInputStream( "readandshow.txt" );
    FileChannel fc = fin.getChannel();
    ByteBuffer buffer = ByteBuffer.allocate( 1024 );
    fc.read( buffer );

您会注意到，我们不需要告诉通道要读 多少数据 到缓冲区中。每一个缓冲区都有复杂的内部统计机制，它会跟踪已经读了多少数据以及还有多少空间可以容纳更多的数据。我们将在 缓冲区内部细节 中介绍更多关于缓冲区统计机制的内容。

写入文件

    FileOutputStream fout = new FileOutputStream( "writesomebytes.txt" );
    FileChannel fc = fout.getChannel();
    ByteBuffer buffer = ByteBuffer.allocate( 1024 );
    for (int i=0; i<message.length; ++i) {
     buffer.put( message[i] );
    }
    buffer.flip();
    c.write( buffer );

注意在这里同样不需要告诉通道要写入多数据。缓冲区的内部统计机制会跟踪它包含多少数据以及还有多少数据要写入。

读写结合

    fcin.read( buffer );
    fcout.write( buffer );
    int r = fcin.read( buffer );
    if (r==-1) {
     break;
    }
    buffer.clear();
    int r = fcin.read( buffer );
    if (r==-1) {
     break;
    }
    buffer.flip();
    fcout.write( buffer );

## 缓冲区 ##

缓冲区buffer有三个重要的属性，用来表示缓冲区内部的工作：

- capacity
- position
- limit

其中，capacity不会变化，position和limit都会在读写模式下改变

**position**

写入buffer：初始化position=0，然后将数据插入position表示的位置并移动position到下一个位置，`0<=position<=capacity-1`

读取buffer：当数据写入buffer后，使用`buffer.flip()`转变为读取模式，即将position位置置为0，limit置为原来position，读取position位置的数据并移动到下一个，`0<=position<=limit`

**limit**

写入buffer：limit==capaticy

读取buffer：limit表示能够从buffer中读取的数据量，使用flip()将limit设置为写入buffer的数据量



![](images/buffers-modes.png)

    // 标记
    private int mark = -1;
    // 当前位置 指向下一个要插入或读取的位置
    private int position = 0;
    // 上界
    private int limit;
    // 缓冲数组容量
    private int capacity;

关系：

Invariants: mark <= position <= limit <= capacity

    // 用于写入前准备
    public final Buffer clear() {
        position = 0;
        limit = capacity;
        mark = -1;
        return this;
    }
    
    // 用于读取
     public final Buffer flip() {
        limit = position;
        position = 0;
        mark = -1;
        return this;
    }
    
    // 用于重写
     public final Buffer rewind() {
        position = 0;
        mark = -1;
        return this;
    }
    
    // 用于标记
    public final Buffer mark() {
        mark = position;
        return this;
    }

可以看到 buff内部都是通过数组指针实现的

### 缓冲区类型

最常用的缓冲区类型是 ByteBuffer。一个 ByteBuffer 可以在其底层字节数组上进行 get/set 操作(即字节的获取和设置)。

ByteBuffer 不是 NIO 中唯一的缓冲区类型。事实上，对于每一种基本 Java 类型都有一种缓冲区类型：

- ByteBuffer
- CharBuffer
- ShortBuffer
- IntBuffer
- LongBuffer
- FloatBuffer
- DoubleBuffer

每一个 Buffer 类都是 Buffer 接口的一个实例。 除了 ByteBuffer，每一个 Buffer 类都有完全一样的操作，只是它们所处理的数据类型不一样。因为大多数标准 I/O 操作都使用 ByteBuffer，所以它具有所有共享的缓冲区操作以及一些特有的操作。

### 缓冲区分配

所有的buffer类都是abstract类型，无法通过new的方式直接创建，可以通过`allocate()`分配一个全新的buffer或`wrap(byte[])`使用已有的byte数组作为缓冲区

**allocate**

```java
ByteBuffer buf = ByteBuffer.allocate(48);
// 其余的buffer类型与ByteBuffer是一样的操作
CharBuffer buf = CharBuffer.allocate(1024);
```

**wrap**

```java
byte[] b = new byte[1024];
ByteBuffer buf = ByteBuffer.wrap(b);
```



ByteBuffer

继承Buffer

    public abstract class ByteBuffer
    extends Buffer
    implements Comparable<ByteBuffer>

可以看到，bytebuffer真正的实现类之一是HeapByteBuffer

    // 底层数组实现
    final byte[] hb;                  // Non-null only for heap buffers
    // 偏移量
    final int offset;
    boolean isReadOnly;   

构造器

    ByteBuffer(int mark, int pos, int lim, int cap,   // package-private
                 byte[] hb, int offset)
    {
        super(mark, pos, lim, cap);
        this.hb = hb;
        this.offset = offset;
    }

创建bytebuffer的方式之一，使用java内部管理的数组形式创建buffer

     public static ByteBuffer allocate(int capacity) {
        if (capacity < 0)
            throw new IllegalArgumentException();
        // super(-1, 0, lim, cap, new byte[cap], 0);
        return new HeapByteBuffer(capacity, capacity);
    }

所以bytebuffer这个抽象类真正的底层实现是HeapByteBuffer

    class HeapByteBuffer
    extends ByteBuffer

HeapByteBuffer的构造器：

    HeapByteBuffer(int cap, int lim) {            // package-private
        super(-1, 0, lim, cap, new byte[cap], 0);
        /*
        hb = new byte[cap];
        offset = 0;
        */
    }

访问方法
访问方法

到目前为止，我们只是使用缓冲区将数据从一个通道转移到另一个通道。然而，程序经常需要直接处理数据。例如，您可能需要将用户数据保存到磁盘。在这种情况下，您必须将这些数据直接放入缓冲区，然后用通道将缓冲区写入磁盘。

或者，您可能想要从磁盘读取用户数据。在这种情况下，您要将数据从通道读到缓冲区中，然后检查缓冲区中的数据。
在本节的最后，我们将详细分析如何使用 ByteBuffer 类的 get() 和 put() 方法直接访问缓冲区中的数据。

- byte get();
- ByteBuffer get( byte dst[] );
- ByteBuffer get( byte dst[], int offset, int length );
- byte get( int index );

具体实现实例：

bytebuffer: public abstract byte get();


    // heapbytebuffer的实现
    public byte get() {
    	return hb[ix(nextGetIndex())];
    }
    
    // buffer中实现
     final int nextGetIndex() {                          // package-private
        if (position >= limit)
            throw new BufferUnderflowException();
        return position++;
    }
    
    // heapbytebuffer的实现
    protected int ix(int i) {
    	return i + offset;
    }

相对 get 方法。读取此缓冲区当前位置的字节，然后该位置递增。

bytebuffer: ByteBuffer get( byte dst[] );

    public ByteBuffer get(byte[] dst) {
        return get(dst, 0, dst.length);
    }
    
    // 采用for调用get()
    public ByteBuffer get(byte[] dst, int offset, int length) {
    	// 检查参数边界是否合理
        checkBounds(offset, length, dst.length);
    	//  如果要获取的数据长度大于缓冲数组剩余的数据长度 就异常
        if (length > remaining())
            throw new BufferUnderflowException();
    	// 终止下标
        int end = offset + length;
        for (int i = offset; i < end; i++)
            dst[i] = get();
        return this;
    }

也是相对get()方法


bytebuffer:public abstract byte get(int index);

    // heapbytebuffer实现
    public byte get(int i) {
    	return hb[ix(checkIndex(i))];
    }
    
    // buffer实现
     final int checkIndex(int i) {                       // package-private
        if ((i < 0) || (i >= limit))
            throw new IndexOutOfBoundsException();
        return i;
    }

前几个 get() 方法是相对的，而最后一个方法是绝对的。 相对 意味着 get() 操作服从 limit 和 position 值 ― 更明确地说，字节是从当前 position 读取的，而 position 在 get 之后会增加。另一方面，一个 绝对 方法会忽略 limit 和 position 值，也不会影响它们。事实上，它完全绕过了缓冲区的统计方法。
前几个 get() 方法是相对的，而最后一个方法是绝对的。 相对 意味着 get() 操作服从 limit 和 position 值 ― 更明确地说，字节是从当前 position 读取的，而 position 在 get 之后会增加。另一方面，一个 绝对 方法会忽略 limit 和 position 值，也不会影响它们。事实上，它完全绕过了缓冲区的统计方法。

类型化的 get() 和 put() 方法

除了前些小节中描述的 get() 和 put() 方法， ByteBuffer 还有用于读写不同类型的值的其他方法，如下所示：

- getByte()
- getChar()
- getShort()
- getInt()
- getLong()
- getFloat()
- getDouble()
- putByte()
- putChar()
- putShort()
- putInt()
- putLong()
- putFloat()
- putDouble()

这里以getInt为例分析底层如何得到int数据：

bytebuffer: public abstract int getInt();
​    
    /**
     * heapbytebuffer实现使用到Bits类 其中bigEndian=true表示默认大端序
     * 最高有效位在最低有效位之前。这样就能理解后面的取值
     */
    public int getInt() {
    	return Bits.getInt(this, ix(nextGetIndex(4)), bigEndian);
    }


    static private int makeInt(byte b3, byte b2, byte b1, byte b0) {
        return (((b3       ) << 24) |
                ((b2 & 0xff) << 16) |
                ((b1 & 0xff) <<  8) |
                ((b0 & 0xff)      ));
    }
    
    static int getIntL(ByteBuffer bb, int bi) {
        return makeInt(bb._get(bi + 3),
                       bb._get(bi + 2),
                       bb._get(bi + 1),
                       bb._get(bi    ));
    }
    
    static int getIntL(long a) {
        return makeInt(_get(a + 3),
                       _get(a + 2),
                       _get(a + 1),
                       _get(a    ));
    }
    
    static int getIntB(ByteBuffer bb, int bi) {
        return makeInt(bb._get(bi    ),
                       bb._get(bi + 1),
                       bb._get(bi + 2),
                       bb._get(bi + 3));
    }
    
    static int getIntB(long a) {
        return makeInt(_get(a    ),
                       _get(a + 1),
                       _get(a + 2),
                       _get(a + 3));
    }
    
    static int getInt(ByteBuffer bb, int bi, boolean bigEndian) {
        return bigEndian ? getIntB(bb, bi) : getIntL(bb, bi) ;
    }

上面代码表示针对大序和小序在前分别处理，最重要的方法makeInt();使用下面的实例表示如何取得int值

    	// 这几个字节表示int 273
    	byte b3 = 0;
    	byte b2 = 0;
    	byte b1 = 1;
    	byte b0 = 17;
    	/**
    	 * 将b3的8bit全部放到int的高8位，(不需要置0)移位其余24位都为0，保留b2的低8位并将其他位置0然后移到16-23位，
    	 * 保留b1的低8位并将其他位置0然后移到8-15位，保留b0的低8位并将高位全部置0。最后将所有按位或保留相应的位，
    	 * 得到对应的int值
    	 */
    	int i = ((b3) << 24) | ((b2 & 0xff) << 16) | ((b1 & 0xff) << 8) | ((b0 & 0xff));

对于所有的get基本数据类型都有相应的make方法，主要的思想差不多，只是取出数组中byte的个数不同而已

至于put方法，将对应的类型值移位到几个byte中，再写入。
​	
    // 两个是Bits方法
    static void putIntB(long a, int x) {
        _put(a    , int3(x));
        _put(a + 1, int2(x));
        _put(a + 2, int1(x));
        _put(a + 3, int0(x));
    }
    
    private static byte int3(int x) { return (byte)(x >> 24); }
    private static byte int2(int x) { return (byte)(x >> 16); }
    private static byte int1(int x) { return (byte)(x >>  8); }
    private static byte int0(int x) { return (byte)(x      ); }
    
    // 都是heapbytebuffer方法
    void _put(int i, byte b) { // package-private
    
    	hb[i] = b;
    
    }
    
    
    public ByteBuffer putInt(int x) {
    
    	Bits.putInt(this, ix(nextPutIndex(4)), x, bigEndian);
    	return this;
    
    }

关于缓冲区的更多内容

本节将讨论使用缓冲区的一些更复杂的方面，比如缓冲区分配、包装和分片。我们还会讨论 NIO 带给 Java 平台的一些新功能。您将学到如何创建不同类型的缓冲区以达到不同的目的，如可保护数据不被修改的 只读 缓冲区，和直接映射到底层操作系统缓冲区的 直接 缓冲区。我们将在本节的最后介绍如何在 NIO 中创建内存映射文件。

缓冲区分配和包装
​    
	// 分配
	ByteBuffer buffer = ByteBuffer.allocate( 1024 );
	// 或者包装
	byte array[] = new byte[1024];
	ByteBuffer buffer = ByteBuffer.wrap( array );

本例使用了 wrap() 方法将一个数组包装为缓冲区。必须非常小心地进行这类操作。一旦完成包装，底层数据就可以通过缓冲区或者直接访问。

底层代码：仍然使用一个heapbytebuffer作为一个底层实现，只不过数组的创建由自己创建，但是这样会使外部具有对缓冲区的访问权，不安全

    public static ByteBuffer wrap(byte[] array) {
        return wrap(array, 0, array.length);
    }
    
     public static ByteBuffer wrap(byte[] array,
                                    int offset, int length)
    {
        try {
            return new HeapByteBuffer(array, offset, length);
        } catch (IllegalArgumentException x) {
            throw new IndexOutOfBoundsException();
        }
    }

缓冲区分片

slice() 方法根据现有的缓冲区创建一种 子缓冲区 。也就是说，它创建一个新的缓冲区，新缓冲区与原来的缓冲区的一部分共享数据。

    ByteBuffer buffer = ByteBuffer.allocate( 10 );
    for (int i=0; i<buffer.capacity(); ++i) {
     buffer.put( (byte)i );
    }
    buffer.position( 3 );
    buffer.limit( 7 );
    ByteBuffer slice = buffer.slice();
    for (int i=0; i<slice.capacity(); ++i) {
     	byte b = slice.get( i );
     	b *= 11;
     	slice.put( i, b );
    }
    buffer.position( 0 );
    buffer.limit( buffer.capacity() );
    
    while (buffer.remaining()>0) {
     System.out.println( buffer.get() );
    }

缓冲区片对于促进抽象非常有帮助。可以编写自己的函数处理整个缓冲区，而且如果想要将这个过程应用于子缓冲区上，您只需取主缓冲区的一个片，并将它传递给您的函数。这比编写自己的函数来取额外的参数以指定要对缓冲区的哪一部分进行操作更容易。

    $ java SliceBuffer
    0
    1
    2
    33
    44
    55
    66
    7
    8
    9

底层代码：

	// 共享一个数组hb，无标记，当前位置pos=0，limit和cap都为剩余数据长度，偏移量pos+offset
	public ByteBuffer slice() {
		return new HeapByteBuffer(hb, -1, 0, this.remaining(), this.remaining(), this.position() + offset);
	}
	
	 public final int remaining() {
	    return limit - position;
	}
	
	// 对应heapbytebuffer的构造器
	protected HeapByteBuffer(byte[] buf, int mark, int pos, int lim, int cap, int off) {
	
		super(mark, pos, lim, cap, buf, off);
		/*
		 * hb = buf; offset = off;
		 */
	
	}

内存映射文件 I/O
内存映射文件 I/O

内存映射文件 I/O 是一种读和写文件数据的方法，它可以比常规的基于流或者基于通道的 I/O 快得多。

内存映射文件 I/O 是通过使文件中的数据神奇般地出现为内存数组的内容来完成的。这其初听起来似乎不过就是将整个文件读到内存中，但是事实上并不是这样。一般来说，只有文件中实际读取或者写入的部分才会送入（或者 映射 ）到内存中。

内存映射并不真的神奇或者多么不寻常。现代操作系统一般根据需要将文件的部分映射为内存的部分，从而实现文件系统。Java 内存映射机制不过是在底层操作系统中可以采用这种机制时，提供了对该机制的访问。

尽管创建内存映射文件相当简单，但是向它写入可能是危险的。仅只是改变数组的单个元素这样的简单操作，就可能会直接修改磁盘上的文件。修改数据与将数据保存到磁盘是没有分开的。

将文件映射到内存

了解内存映射的最好方法是使用例子。在下面的例子中，我们要将一个 FileChannel (它的全部或者部分)映射到内存中。为此我们将使用 FileChannel.map() 方法。下面代码行将文件的前 1024 个字节映射到内存中：

MappedByteBuffer mbb = fc.map( FileChannel.MapMode.READ_WRITE,
     0, 1024 );

map() 方法返回一个 MappedByteBuffer，它是 ByteBuffer 的子类。因此，您可以像使用其他任何 ByteBuffer 一样使用新映射的缓冲区，操作系统会在需要时负责执行行映射



## 使用

