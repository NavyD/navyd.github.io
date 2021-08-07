# Could not autowire. No beans of 'ProductCategoryMapper' type found

## 描述

springboot整合mybatis mapper注入时显示could not autowire的错误，不影响使用. `idea iu 2020.1.2`

![](../assets/images/0dc0cc3d-5057-47e8-9620-25b90ce05686.png)

## 方案

- 直接关掉IDEA的警告提示

修改idea配置，将spring 的severity的值设置为"warning", 如下：

![](../assets/images/5abca38d-d976-4deb-86a3-dfe9f824858f.jpg)

- @Autowried注解设置required=false

```java
@Autowired(required = false)
private CarUserMapper carUserMapper;
```

这样就不会警告了。因为此时 @Autowried 不会再去校验 Mapper 接口是否为空。

缺点：每引入一个Mapper接口都需要设置上required=false，相当的麻烦，而且容易给别人造成误解：这个Mapper接口真的不需一定存在。

- @Autowried替换为@Resource

```java
@Resource
private CarUserMapper carUserMapper;
```

此时也不会给红色警告了。@Resource 注解是 J2EE 提供的，而 @Autowried 注解是 Spring 提供的，他们如果感兴趣可以去看一下他们的区别。

- 在Mapper接口上加@Component

```java
@Mapper
@Component
public inteface CarUserMapper{}
```

加这个注解呢，主要是为了让欺骗IEDA，让它以为CarUserMapper也是一个Spring管理的Bean，这样子使用@Autowired注解注入也不会报错了。

- 使用构造函数注入（Spring4.x推荐）

相信大家都有使用Lombok这个神器了，我们可以利用他的注解@RequiredArgsConstructor来直接构建构造函数即可，不过我尝试过单单使用@AllArgsConstructor也是没问题的。

当然了，大家如果注入的依赖比较少或者闲得蛋疼，还是可以自己来写构造函数的。

```java
@Service
@RequiredArgsConstructor(onConstructor = @__(@Autowired))
//@AllArgsConstructor
public class ChargeServiceImpl implements ChargeService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final CarUserMapper carUserMapper;
    private final ChargingMapper chargingMapper;
}
```

参考：

- [IDEA提示找不到Mapper接口：Could not autowire.No beans of 'xxxMapper' type found](https://www.cnblogs.com/Howinfun/p/11731826.html)
- [mybatis+spring boot, mapper 提示Could not autowire. No beans of … type found](https://www.cnblogs.com/cristin/p/7771817.html)
