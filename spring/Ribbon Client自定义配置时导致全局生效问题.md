# Ribbon Client自定义配置时导致全局生效问题

## 描述

在对指定的service进行局部定义负载均衡算法时，出现其它客户端也用了当前定义的负载均衡算法

```java
@RibbonClient(name = "user-center", configuration = UserCenterConfiguration.CustomConfiguration.class)
static class UserCenterConfiguration {
    @Configuration
    public static class CustomConfiguration {
        @Bean
        public IRule iRule() {
            return new RandomRule();
        }
    }
}
```

## 原因

spring 父子上下文重叠扫描

一般我们在Spring的配置文件application.xml中对Service层代码配置事务管理，可以对Service的方法进行AOP增强或事务处理如事务回滚，但是遇到一个问题，在Controller类中调用Service层方法，配置的事务管理会失效，查询相关资料发现原因。其实Spring和SpringMVC俩个容器为父子关系，Spring为父容器，而SpringMVC为子容器。也就是说application.xml中应该负责扫描除@Controller的注解如@Service，而SpringMVC的配置文件应该只负责扫描@Controller，否则会产生重复扫描导致Spring容器中配置的事务失效。

因此正确的配置方式应该为：

Spring的配置文件：application.xml

```xml
<context:component-scan base-package="org.bc.redis" use-default-filters="true">
    <!-- 排除含@Controller注解的类 -->
    <context:exclude-filter type="annotation" expression="org.bc.redis.controller.UserController"/>
</context:component-scan>
```

或者

```xml
<!-- 指定扫描的包,避开包含@Controller注解的包 -->
<context:component-scan base-package="org.bc.redis.service" use-default-filters="true">
</context:component-scan>
```

SpringMVC的配置文件：springmvc.xml

```xml
<!--  只扫描含@Controller注解的包,避免重复扫描 -->
<context:component-scan base-package="org.bc.redis.controller" use-default-filters="true">
</context:component-scan>
```

最后经过测试，其实问题主要在于SpringMVC的配置文件扫包范围，Spring的配置文件就算也扫了@Controller注解，但是在SpringMVC会重新扫描一次，事务管理的Service只要没被重新扫描就不会出现事务失效问题

## 解决

The CustomConfiguration class must be a @Configuration class, but take care that it is not in a @ComponentScan for the main application context. Otherwise, it is shared by all the @RibbonClients. If you use @ComponentScan (or @SpringBootApplication), you need to take steps to avoid it being included (for instance, you can put it in a separate, non-overlapping package or specify the packages to scan explicitly in the @ComponentScan).

### Java注解

分离与`@SpringBootApplication`在不同层次

```java
package xyz.navyd.app;

@RibbonClient(name = "user-center", configuration = xyz.navyd.ribbonconfig.CustomConfiguration.class)
static class UserCenterConfiguration {

}

package xyz.navyd.ribbonconfig;

@Configuration
public static class CustomConfiguration {
    @Bean
    public IRule iRule() {
        return new RandomRule();
    }
}
```

### Properties

To set the IRule for a service name called users, you could set the following properties:

```yml
users:
  ribbon:
    NFLoadBalancerRuleClassName: com.netflix.loadbalancer.WeightedResponseTimeRule
```

参考：

- [Spring+SpringMVC 配置事务管理无效原因及解决方案。](https://blog.csdn.net/qq_32588349/article/details/52097943)
- [Customizing the Ribbon Client](https://docs.spring.io/spring-cloud/docs/Hoxton.SR8/reference/htmlsingle/#customizing-the-ribbon-client)
- [Customizing the Ribbon Client by Setting Properties](https://docs.spring.io/spring-cloud/docs/Hoxton.SR8/reference/htmlsingle/)
