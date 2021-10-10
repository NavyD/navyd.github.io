// var totalPages;//总页数
// var pageno = 1;//当前页数
// var C = 10;//滚动条距离底部的距离
// $(function () {
//     let posts = $("#posts");
//     let totalPages = $("#lastpage").attr("total");
//     $(window).scroll(function () {
//         var scrollTop = $(this).scrollTop(), scrollHeight = $(document).height(), windowHeight = $(this).height();
//         var positionValue = (scrollTop + windowHeight) - scrollHeight;
//         if (positionValue >= -C) {
//             //do something
//             if (pageno < totalPages) {
//                 pageno++;
//                 doSomething(pageno);
//             } else {
//                 alert('没有更多了');
//             }
//         }
//     });


//     function doSomething(pageno) {
//         var url = "/page/" + pageno;//分页列表的接口
//         console.log("url: ", url);
//         $.get(url, (data) => {
//             let nextPosts = $(data).find("#posts");
//             console.log("data: ", nextPosts);
//             posts.append(nextPosts);
//         })
//     }
// });

$(document).ready(function () {
    $(function () {
        let posts = $("#posts");
        var pageNum = $("#mescroll").attr("page-number");//当前页数
        let totalPages = $("#mescroll").attr("total-pages");
        console.log("totalPages: " + totalPages + " page number: " + pageNum);
        var mescroll = new MeScroll("mescroll", {
            down: {
                callback: downCallback //下拉刷新的回调,别写成downCallback(),多了括号就自动执行方法了
            },
            up: {
                callback: upCallback,
                //以下是一些常用的配置,当然不写也可以的.
                page: {
                    num: 1, //当前页 默认0,回调之前会加1; 即callback(page)会从1开始
                    size: 10 //每页数据条数,默认10
                },
                htmlNodata: '<p class="upwarp-nodata">-- END --</p>',
                noMoreSize: 3, //如果列表已无数据,可设置列表的总数量要大于5才显示无更多数据;
                // toTop: {
                //     //回到顶部按钮
                //     src: "../img/mescroll-totop.png", //图片路径,默认null,支持网络图
                //     offset: 1000 //列表滚动1000px才显示回到顶部按钮	
                // },
                // empty: {
                //     //列表第一页无任何数据时,显示的空提示布局; 需配置warpId才显示
                //     warpId: "xxid", //父布局的id (1.3.5版本支持传入dom元素)
                //     icon: "../img/mescroll-empty.png", //图标,默认null,支持网络图
                //     tip: "暂无相关数据~" //提示
                // },
                loadFull: {
                    use: true, //列表数据过少,是否自动加载下一页,直到满屏或者无更多数据为止;默认false
                    delay: 500 //延时执行的毫秒数; 延时是为了保证列表数据或占位的图片都已初始化完成,且下拉刷新上拉加载中区域动画已执行完毕;
                },
                lazyLoad: {
                    use: true, // 是否开启懒加载,默认false
                    // attr: 'imgurl' // 标签中网络图的属性名 : <img imgurl='网络图  src='占位图''/>
                }
            }
        });

        function downCallback() {
            mescroll.endSuccess(); //无参. 注意结束下拉刷新是无参的
        }

        //下拉刷新的回调
        function upCallback(page) {
            var url = "/page/" + page.num;//分页列表的接口
            console.log("call url: " + url);
            $.ajax({
                url: url,
                success: (data) => {
                    // console.log("got data: ", data);
                    let nextPosts = $(data).find("#posts").children();
                    let size = $(data).find("#mescroll").attr("page-size");
                    console.log("got pageSize: " + size);
                    mescroll.endByPage(size, totalPages);

                    posts.append(nextPosts);
                },
                error: function (data) {
                    console.error("failed data: ", data);
                    //联网失败的回调,隐藏下拉刷新的状态
                    mescroll.endErr();
                }
            })
        }
    });

});

