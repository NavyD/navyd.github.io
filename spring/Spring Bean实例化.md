# Spring Bean实例化

## 实例化方式

### 构造器

```xml
<bean id="person" class="com.dfdc.spring.demo.Person"></bean>
<bean id="personWithParam" class="com.dfdc.spring.demo.Person">
    <constructor-arg name="name" value="等风的草"/>
</bean>
```

### 静态工厂方法

```xml

<!-- 静态方法实例化 Bean -->
 <bean id="user-by-static-method" class="org.geekbang.thinking.in.spring.ioc.overview.domain.User"
       factory-method="createUser"/>
```

```java
public class User {

    private Long id;

    private String name;

    public static User createUser() {
        User user = new User();
        user.setId(1L);
        user.setName("小马哥");
        return user;
    }
}

public static void main(String[] args) {
    // 配置 XML 配置文件
    // 启动 Spring 应用上下文
    BeanFactory beanFactory = new ClassPathXmlApplicationContext("classpath:/META-INF/bean-instantiation-context.xml");
    User user = beanFactory.getBean("user-by-static-method", User.class);
}
```

### Bean 工厂方法

```xml
<!-- 实例（Bean）方法实例化 Bean -->
<bean id="user-by-instance-method" factory-bean="userFactory" factory-method="createUser"/>

<bean id="userFactory" class="org.geekbang.thinking.in.spring.bean.factory.DefaultUserFactory"/>
```

```java
BeanFactory beanFactory = new ClassPathXmlApplicationContext("classpath:/META-INF/bean-instantiation-context.xml");

User userByInstanceMethod = beanFactory.getBean("user-by-instance-method", User.class);
```

### FactoryBean

```java

public class UserFactoryBean implements FactoryBean {

    @Override
    public Object getObject() throws Exception {
        return User.createUser();
    }

    @Override
    public Class<?> getObjectType() {
        return User.class;
    }
}
```

```xml
<bean id="user-by-factory-bean" class="org.geekbang.thinking.in.spring.bean.factory.UserFactoryBean" />
```
