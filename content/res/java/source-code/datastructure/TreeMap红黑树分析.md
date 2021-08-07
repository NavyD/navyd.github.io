红黑树是一种近似平衡的二叉查找树，它能够确保任何一个节点的左右子树的高度差不会超过二者中较低那个的一陪。具体来说，红黑树是满足如下条件的二叉查找树（binary search tree）：

 1. 每个节点要么是红色，要么是黑色。 
 2. 根节点必须是黑色 
 3. 红色节点不能连续（也即是，红色节点的孩子和父亲都不能是红色）。
 4. 对于每个节点，从该点至null（树尾端）的任何路径，都含有相同个数的黑色节点。

在树的结构发生改变时（插入或者删除操作），往往会破坏上述条件3或条件4，需要通过调整使得查找树重新满足红黑树的约束条件。

下面结合Java.util.TreeMap的代码解释。

左旋：左旋操作用于将一个向右倾斜的红色链接旋转为向左链接。即父节点对着右子节点旋转

![左旋转](http://img.blog.csdn.net/20171015125136318?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
```
	 /**
     * 左旋转后，除了p的key value没有改变，p变为左孩子节点的位置，p本来的右孩子节点变为p的位置
     */
    private void rotateLeft(Entry<K,V> p) {
        if (p != null) {
            Entry<K,V> r = p.right;
            p.right = r.left;
            if (r.left != null)
                r.left.parent = p;
            r.parent = p.parent;
            if (p.parent == null)
                root = r;
            else if (p.parent.left == p)
                p.parent.left = r;
            else
                p.parent.right = r;
            r.left = p;
            p.parent = r;
        }
    }
```

右旋：即父节点对着左子节点旋转
![右旋转](http://img.blog.csdn.net/20171015125633973?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

```
	/**
     * 右旋转后，除了p的key value没有改变，p变为右孩子节点的位置，p本来的左孩子节点变为p的位置
     */
    private void rotateRight(Entry<K,V> p) {
        if (p != null) {
            Entry<K,V> l = p.left;
            p.left = l.right;
            if (l.right != null) l.right.parent = p;
            l.parent = p.parent;
            // 父节点连接方式
            if (p.parent == null)
                root = l;
            else if (p.parent.right == p)
                p.parent.right = l;
            else p.parent.left = l;
            l.right = p;
            p.parent = l;
        }
    }
```
RBTree的插入操作
RBTree的插入与BST的插入方式是一致的，只不过是在插入过后，可能会导致树的不平衡，这时就需要对树进行旋转操作和颜色修复（在这里简称插入修复），使得它符合RBTree的定义。
新插入的节点是一定红色的，插入修复时如果父节点的颜色为黑终止修复操作。即只有在***父节点为红色节点***的时候是需要插入修复操作的。
插入修复操作分为以下的三种情况，而且新插入的节点的父节点都是红色的：

 1. x的父亲节点与x的叔父节点都为红色 
 2. x是父节点的右孩子，x的父亲节点为红色，且x的叔父节点是黑色
 3. x是父节点的左孩子。x的父亲节点为红色，且x的叔父节点是黑色

插入操作-1：x的父亲节点与x的叔父节点都为红色 
1的操作是将**祖父节点变为红，父亲和叔父节点变黑**。即维持了高度的平衡，修复后颜色也符合RBTree定义的第三条和第四条。**操作完成后G(祖父节点)节点变成了新的节点。如果G节点的父节点是红色的话，则继续做修复操作**。如下图：
![这里写图片描述](http://img.blog.csdn.net/20171015131457124?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
祖父节点变为红，父亲和叔父节点变黑后。新节点n为原祖父节点，n的父节点为红，继续修复：
![这里写图片描述](http://img.blog.csdn.net/20171015131626045?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

插入操作-2：x是父节点的右孩子，x的父亲节点为红色，且x的叔父节点是黑色
2的操作是将**x节点的父节点进行右旋操作，转换为插入操作-3**。如下图

![这里写图片描述](http://img.blog.csdn.net/20171015132349643?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
将x节点的父节点进行右旋操作后：
![这里写图片描述](http://img.blog.csdn.net/20171015133205915?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

插入操作-3：x是父节点的左孩子。x的父亲节点为红色，且x的叔父节点是黑色
3的操作是将**x的父节点变为黑色，x的祖父节点变为红色，把x的祖父节点右旋**。如下图

![这里写图片描述](http://img.blog.csdn.net/20171015133653134?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
x的父节点变为黑色，x的祖父节点变为红色，把x的祖父节点右旋
![这里写图片描述](http://img.blog.csdn.net/20171015133940350?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

插入操作总结：
插入是一个向上修复的操作。让所有节点符合红黑树的定义，由于x节点和其父节点都是红色，必然要将父节点变黑，但是增加一个黑色节点必然不符合定义4，那么就需要向上将某个黑色节点变红，但是有可能不符合定义3，出现连续的两个红色节点，必须向上不断修复。
所以***插入操作是对x节点的父节点，叔父节点，祖父节点向上的节点不断修复***，直到x的节点符合定义为止

treemap的修复插入代码：
```
    /**
     * 修复插入大概分三种情况：
     * 0.x的父节点是黑色就不用修复
     * 1.x的父亲节点与x的叔父节点都为红色，只需将x的父亲和叔父都变为黑色。x的祖父变为红色
     * 2.x是父节点的右孩子，x的父亲节点为红色，且x的叔父节点是黑色， 将x的父节点左旋转成为一边连续的两个红节点 变为 情况3
     * 3.x是父节点的左孩子。x的父亲节点为红色，且x的叔父节点是黑色，将x的父节点变为黑色，x的祖父节点变为红色。
     * 将x的祖父节点右旋转。将x原来的祖父节点变为x的兄弟节点，3完成后一定退出循环，x的父节点为黑，祖父节点也为黑
     *
     * x的父节点是祖父节点的左 右孩子需要分开处理，这是对称的
     * @param x
     * @author Navy D
     * @date 20171007143615
     */
    private void fixAfterInsertion(Entry<K,V> x) {
    	// 将新节点作为红色节点
        x.color = RED;
        // 新插入的结点都是红色的。如果其父结点是黑色的，那就什么都不用做
        while (x != null && x != root && x.parent.color == RED) {
        	// 如果x的父亲是x的祖父的左孩子	x与其父节点p都是红节点。且x的叔父节点是红色
            if (parentOf(x) == leftOf(parentOf(parentOf(x)))) {
            	// x的父亲的兄弟节点  叔父节点
                Entry<K,V> y = rightOf(parentOf(parentOf(x)));
                // 1.如果x的父亲节点与x的叔父节点都为红色。将x的父亲和叔父都变为黑色。x的祖父变为红色
                if (colorOf(y) == RED) {
                    setColor(parentOf(x), BLACK);
                    setColor(y, BLACK);
                    setColor(parentOf(parentOf(x)), RED);
                    x = parentOf(parentOf(x));
                }
                // 如果x的父亲节点是红色，叔父节点是黑色
                else {
                	/**
                	 *  2.x是父节点的右孩子，x的父亲节点为红色，且x的叔父节点是黑色，
                	 *  将x的父节点左旋转成为左边连续的两个红节点 变为 情况3
                	 */
                    if (x == rightOf(parentOf(x))) {
                        x = parentOf(x);
                       // 注意x变为父节点后旋转又成为孩子节点
                        rotateLeft(x);
                    }

                    /**
                     *  3.x是父节点的左孩子。x的父亲节点为红色，且x的叔父节点是黑色，将x的父节点变为黑色，
                     *  x的祖父节点变为红色。将x的祖父节点右旋转。将x原来的祖父节点变为x的兄弟节点
                     */
                    setColor(parentOf(x), BLACK);
                    setColor(parentOf(parentOf(x)), RED);
                    rotateRight(parentOf(parentOf(x)));
                }
            }
            // 如果x的父亲节点是祖父的右孩子
            else {
            	// x的叔父节点
                Entry<K,V> y = leftOf(parentOf(parentOf(x)));
                /**
                 * 4.如果x的父亲节点与叔父节点都是红色，就将x的父亲节点与叔父节点变黑，祖父节点变红
                 */
                if (colorOf(y) == RED) {
                    setColor(parentOf(x), BLACK);
                    setColor(y, BLACK);
                    setColor(parentOf(parentOf(x)), RED);
                    x = parentOf(parentOf(x));
                } else {
                	/**
                	 * 5.如果x是父亲节点的左孩子，且父亲节点是红色，叔父节点是黑色，就将父节点右旋转
                	 * 变为右边连续的两个红节点 转变为情况6
                	 */
                    if (x == leftOf(parentOf(x))) {
                        x = parentOf(x);
                        rotateRight(x);
                    }
                    /**
                     * 6.如果x是父亲的右孩子，且父亲节点是红色，叔父节点是黑色，将x的父节点变为黑色，
                     *  x的祖父节点变为红色。将x的祖父节点左旋转。将x原来的祖父节点变为x的兄弟节点
                     */
                    setColor(parentOf(x), BLACK);
                    setColor(parentOf(parentOf(x)), RED);
                    rotateLeft(parentOf(parentOf(x)));
                }
            }
        }
        // root节点保持为黑色
        root.color = BLACK;
    }
```

删除操作：
删除操作首先需要做的也是BST的删除操作，**删除操作会删除对应的节点，如果是叶子节点就直接删除，如果是非叶子节点，使用左子树中的最大节点替换这个删除节点的位置，如果左子树为空，就使用右子树中最小节点替换这个删除节点。**删除后就需要做删除修复操作，使的树符合红黑树的定义，符合定义的红黑树高度是平衡的。

修复操作：
删除操作的总体思想是从兄弟节点借调黑色节点使树保持局部的平衡，如果局部的平衡达到了，就看整体的树是否是平衡的，如果不平衡就接着向上追溯调整。
**如果删除节点x是红色节点就不用修复。故x一定是黑色节点**
删除修复操作分为四种情况(删除黑节点后)：
注意这个针对x是用父节点左孩子，x是右孩子的情况是左孩子的映射。

 1. x节点的兄弟节点是红色的节点。 
 2. x节点的兄弟节点是黑色的节点，且兄弟节点的子节点都是黑色的。
 3. x的兄弟节点是黑色，且x的兄弟节点中左孩子为红色，右孩子为黑色
 4.x的兄弟节点是黑色，且x的兄弟节点中左孩子为任意颜色，右孩子为红色

删除操作-1：x节点的兄弟节点是红色的节点。 
**将x的兄弟节点变黑，x的父节点变红，左旋转父节点使新的兄弟节点变为黑色**，转换为情况234。由于兄弟节点是红色节点的时候，无法借调黑节点，所以需要将兄弟节点提升到父节点，由于兄弟节点是红色的，根据RBTree的定义，兄弟节点的子节点是黑色的，就可以从它的子节点借调了。镜像结构的树只需要做对应的右旋操作即可。
之所以要做1操作是因为兄弟节点是红色的，无法借到一个黑节点来填补删除的黑节点。如下图：
![这里写图片描述](http://img.blog.csdn.net/20171015142450918?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
将x的兄弟节点变黑，x的父节点变红，左旋转父节点使新的兄弟节点变为黑色：
![这里写图片描述](http://img.blog.csdn.net/20171015142546854?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

删除操作-2：x节点的兄弟节点是黑色的节点，且兄弟节点的子节点都是黑色的。
**将x的兄弟节点变红色即可，将父节点变成新的x节点，继续向上调整**。2的删除操作是由于兄弟节点可以消除一个黑色节点，(删除的节点为黑色，故删除这一边少一个黑色节点，需要兄弟那边也少一个黑色节点平衡)因为兄弟节点和兄弟节点的子节点都是黑色的，所以可以将兄弟节点变红，这样就可以保证树的局部的颜色符合定义了。这个时候需要*将父节点A变成新的节点，继续向上调整*，直到整颗树的颜色符合RBTree的定义为止。
case 2这种情况下之所以要将兄弟节点变红，是因为如果把兄弟节点借调过来，会导致兄弟的结构不符合RBTree的定义，这样的情况下只能是将兄弟节点也变成红色来达到颜色的平衡。当将兄弟节点也变红之后，达到了局部的平衡了，但是对于祖父节点来说是不符合定义4的。这样就需要回溯到父节点，接着进行修复操作。
注意：treemap中当由情况1进入情况2时，删除节点x的父节点为红，兄弟节点也为红，向上调整x = parentOf(x)后x为红色，必定退出循环，最后setColor(x, BLACK)。也就是说删除操作2修复后如果父节点为红色就说明左右子节点黑色节点数已经平衡(删除节点一边少一个黑色节点，修复变红后使兄弟节点一边同样少一个黑节点)，只需要将父节点变黑就能是整个树黑色节点树平衡。如果父节点为黑色就无法确定祖父节点是否平衡
![这里写图片描述](http://img.blog.csdn.net/20171015151619276?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
将x的兄弟节点变红色即可，将父节点变成新的x节点
![这里写图片描述](http://img.blog.csdn.net/20171015151725403?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
注意：这两个图不标准，B不可能为根节点，即b上边还有节点，根节点不可能为红色

删除操作-3：x的兄弟节点是黑色，且x的兄弟节点中左孩子为红色，右孩子为黑色
**将兄弟节点的左孩子为黑色，兄弟节点变为红色，右旋转兄弟节点**，新的兄弟节点还为黑色 ，其右孩子为红色****，3的删除操作是一个中间步骤，它的目的是将左边的红色节点借调过来使右边节点为红色，这样就可以转换成4状态了，通过将两个节点变成黑色来保证红黑树的整体平衡。
之所以说3是一个中间状态，是因为根据红黑树的定义来说，下图并不是平衡的，他是*通过2操作完后向上回溯出现的状态*。之所以会出现3和后面的4的情况，是因为可以通过借用侄子节点的红色，变成黑色来符合红黑树定义4.
![这里写图片描述](http://img.blog.csdn.net/20171015153049034?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
兄弟节点的左孩子为黑色，兄弟节点变为红色，右旋转兄弟节点
![这里写图片描述](http://img.blog.csdn.net/20171015153120207?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

删除操作-4：x的兄弟节点是黑色，且x的兄弟节点中左孩子为任意颜色，右孩子为红色
**将x的兄弟节点变为父节点的颜色，兄弟节点的右子节点变黑，x的父节点变为黑色，并左旋转父节点**
4的操作是真正的节点借调操作，通过将兄弟节点以及兄弟节点的右节点借调过来，并将兄弟节点的右子节点变成红色来达到借调两个黑节点的目的，这样的话，整棵树还是符合RBTree的定义的。
4这种情况的发生只有在待删除的节点的兄弟节点为黑，且子节点不全部为黑，才有可能借调到两个节点来做黑节点使用，从而保持整棵树都符合红黑树的定义。
![这里写图片描述](http://img.blog.csdn.net/20171015155359516?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
将x的兄弟节点变为父节点的颜色，兄弟节点的右子节点变黑，x的父节点变为黑色，并左旋转父节点
![这里写图片描述](http://img.blog.csdn.net/20171015155418494?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTmF2eV9EVA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

删除总结：
红黑树的删除操作是最复杂的操作，复杂的地方就在于当删除了黑色节点的时候，如何从兄弟节点去借调节点，以保证树的颜色符合定义。由于红色的兄弟节点是没法借调出黑节点的，这样只能通过选择操作让他上升到父节点，而由于它是红节点，所以它的子节点就是黑的，可以借调。

对于兄弟节点是黑色节点的可以分成3种情况来处理，当所以的兄弟节点的子节点都是黑色节点时，可以直接将兄弟节点变红，这样局部的红黑树颜色是符合定义的。但是整颗树不一定是符合红黑树定义的，需要往上追溯继续调整。

对于兄弟节点的子节点为左红右黑或者 (全部为红，右红左黑)这两种情况，可以先将前面的情况通过选择转换为后一种情况，在后一种情况下，因为兄弟节点为黑，兄弟节点的右节点为红，可以借调出两个节点出来做黑节点，这样就可以保证删除了黑节点，整棵树还是符合红黑树的定义的，因为黑色节点的个数没有改变。

红黑树的删除操作是遇到删除的节点为红色，或者追溯调整到了root节点，这时删除的修复操作完毕。
```
/**
     * x节点分为父节点左孩子与右孩
     * 删除修复重点在于将删除节点的兄弟节点变为黑色，和兄弟节点的孩子的颜色需要符合规则
     * 0.x如果是红色节点就不用修复。故x一定是黑色节点
     *
     * 1.如果x的兄弟节点是红色(父节点为黑色，兄弟其原孩子节点必为黑)，就将父节点变为红色左旋转使新的兄弟节点变为黑色
     * 转变为兄弟节点为黑色的情况(可以进入234)
     * 2.如果x的兄弟节点是黑色，且x的兄弟节点的两个孩子都是黑色，就改变这个兄弟节点为红色 (进入2就不会进入3。4情况)
     * 3.如果x的兄弟节点是黑色，且x的兄弟节点中左孩子为红色，右孩子为黑色，改变兄弟节点左孩子为黑色，兄弟节点变为红色
     * 并右旋转兄弟节点，新的兄弟节点还为黑色 ，其右孩子为红色(如果进入3必然进入4)
     * 4.如果x的兄弟节点是黑色，且x的兄弟节点中左孩子为任意颜色，右孩子为红色，就兄弟节点变为父节点的颜色，父节点变黑，
     * 兄弟节点的右孩子变黑，左旋父节点
     */
    private void fixAfterDeletion(Entry<K,V> x) {
        while (x != root && colorOf(x) == BLACK) {
        	// 如果x节点是父亲节点的左孩子
            if (x == leftOf(parentOf(x))) {
            	// x节点的兄弟节点
                Entry<K,V> sib = rightOf(parentOf(x));
                /**
                 * 1.如果x的兄弟节点为红色，父亲节点一定为黑色(不能连续两个红)，将x的兄弟节点变黑，父节点变红，将父节点左旋转
                 * 降级为原右孩子节点(成为x的叔父节点)的左孩子节点。x的兄弟节点变为x的祖父节点。不平衡
                 * x的新兄弟节点一定为黑色(原兄弟节点为红，两个子节点必定为黑，旋转后左子节点变为新的兄弟节点)
                 */
                if (colorOf(sib) == RED) {
                    setColor(sib, BLACK);
                    setColor(parentOf(x), RED);
                    rotateLeft(parentOf(x));
                    // 新的兄弟节点
                    sib = rightOf(parentOf(x));
                }
                /**
                 * 2.如果x的兄弟节点的左右孩子为黑色就将这个兄弟节点变为红色
                 */
                if (colorOf(leftOf(sib))  == BLACK &&
                    colorOf(rightOf(sib)) == BLACK) {
                    setColor(sib, RED);
                    // 向上寻找 如果是1开始到2一定会退出循环（因为x原本的兄弟节点两孩子为黑色，左孩子为x的新兄弟节点）
                    // 即x的兄弟节点为黑色(改变后为红色)，两个孩子为黑色，x的父节点是左旋后的红色父节点
                    x = parentOf(x);
                }
                // 如果x的兄弟节点的孩子中含有红色节点
                else {
                	/**
                	 * 3.如果x的兄弟节点的右孩子是黑色，左孩子是红色，将x的兄弟的左孩子变为黑色，x的兄弟变为红色，
                	 * 右旋转x的兄弟节点
                	 */
                    if (colorOf(rightOf(sib)) == BLACK) {
                        setColor(leftOf(sib), BLACK);
                        setColor(sib, RED);
                        rotateRight(sib);
                        // 旋转后新的兄弟节点
                        sib = rightOf(parentOf(x));
                    }
                    /**
                     * 4：当前节点是黑色的，且兄弟节点是黑色的，且兄弟节点的右子节点是红色，左子节点任意颜色
                     */
                    setColor(sib, colorOf(parentOf(x)));
                    setColor(parentOf(x), BLACK);
                    setColor(rightOf(sib), BLACK);
                    rotateLeft(parentOf(x));
                    x = root;
                }
            } else { // symmetric
                Entry<K,V> sib = leftOf(parentOf(x));

                if (colorOf(sib) == RED) {
                    setColor(sib, BLACK);
                    setColor(parentOf(x), RED);
                    rotateRight(parentOf(x));
                    sib = leftOf(parentOf(x));
                }

                if (colorOf(rightOf(sib)) == BLACK &&
                    colorOf(leftOf(sib)) == BLACK) {
                    setColor(sib, RED);
                    x = parentOf(x);
                } else {
                    if (colorOf(leftOf(sib)) == BLACK) {
                        setColor(rightOf(sib), BLACK);
                        setColor(sib, RED);
                        rotateLeft(sib);
                        sib = leftOf(parentOf(x));
                    }
                    setColor(sib, colorOf(parentOf(x)));
                    setColor(parentOf(x), BLACK);
                    setColor(leftOf(sib), BLACK);
                    rotateRight(parentOf(x));
                    x = root;
                }
            }
        }

        setColor(x, BLACK);
    }
```


----------
参考：

- [【数据结构和算法05】 红-黑树（看完包懂~）](http://blog.csdn.net/eson_15/article/details/51144079)
- [教你初步了解红黑树](http://blog.csdn.net/v_JULY_v/article/details/6105630)
- [红黑树深入剖析及Java实现](https://zhuanlan.zhihu.com/p/24367771)
- [TreeSet and TreeMap](https://github.com/CarpenterLee/JCFInternals/blob/master/markdown/5-TreeSet%20and%20TreeMap.md)


----------
这是本人第一篇文章，整理这篇文章的动机在于红黑树有些复杂，尽管当时能够理解，可是过了一段时间后就忘记的差不多了，我不求能够有多少作用，只要能让我再看懂就行了

