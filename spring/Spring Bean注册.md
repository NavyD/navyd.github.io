# Spring Bean注册

都是通过`BeanDefinitionRegistry.registerBeanDefinition`注册

## BeanDefinitionRegistry

### Java注解

#### @Bean

```java
public static class Config {

    // 1. 通过 @Bean 方式定义

    /**
     * 通过 Java 注解的方式，定义了一个 Bean
     */
    @Bean(name = {"user", "xiaomage-user"})
    public User user() {
        User user = new User();
        user.setId(1L);
        user.setName("小马哥");
        return user;
    }
}

// 创建 BeanFactory 容器
AnnotationConfigApplicationContext applicationContext = new AnnotationConfigApplicationContext();
// 注册 Configuration Class（配置类）
applicationContext.register(Config.class);
// 启动 Spring 应用上下文
applicationContext.refresh();

// 按照类型依赖查找
// Config 类型的所有 Beans{annotationBeanDefinitionDemo.Config=org.geekbang.thinking.in.spring.bean.definition.AnnotationBeanDefinitionDemo$Config@453da22c}
// User 类型的所有 Beans{user=User{id=1, name='小马哥', city=null, workCities=null, lifeCities=null, configFileLocation=null, company=null, context=null, contextAsText='null', beanName='user'}}
System.out.println("Config 类型的所有 Beans" + applicationContext.getBeansOfType(Config.class));
System.out.println("User 类型的所有 Beans" + applicationContext.getBeansOfType(User.class));
```

未@Compoennt的Config也是Bean

#### @Component

```java
@Component // 定义当前类作为 Spring Bean（组件）
public static class Config {

    // 1. 通过 @Bean 方式定义

    /**
     * 通过 Java 注解的方式，定义了一个 Bean
     */
    @Bean(name = {"user", "xiaomage-user"})
    public User user() {
        User user = new User();
        user.setId(1L);
        user.setName("小马哥");
        return user;
    }
}

// 创建 BeanFactory 容器
AnnotationConfigApplicationContext applicationContext = new AnnotationConfigApplicationContext();
// 注册 Configuration Class（配置类）
applicationContext.register(Config.class);
// 启动 Spring 应用上下文
applicationContext.refresh();

// 按照类型依赖查找
// Config 类型的所有 Beans{annotationBeanDefinitionDemo.Config=org.geekbang.thinking.in.spring.bean.definition.AnnotationBeanDefinitionDemo$Config@453da22c}
// User 类型的所有 Beans{user=User{id=1, name='小马哥', city=null, workCities=null, lifeCities=null, configFileLocation=null, company=null, context=null, contextAsText='null', beanName='user'}}
System.out.println("Config 类型的所有 Beans" + applicationContext.getBeansOfType(Config.class));
System.out.println("User 类型的所有 Beans" + applicationContext.getBeansOfType(User.class));
```

都是Bean

#### @Import

```java
@Import(AnnotationBeanDefinitionDemo.Config.class)
public class AnnotationBeanDefinitionDemo {

    public static void main(String[] args) {
        // 创建 BeanFactory 容器
        AnnotationConfigApplicationContext applicationContext = new AnnotationConfigApplicationContext();
        // 注册 Configuration Class（配置类）
        applicationContext.register(AnnotationBeanDefinitionDemo.class);

        // 通过 BeanDefinition 注册 API 实现
        // 1.命名 Bean 的注册方式
//        registerUserBeanDefinition(applicationContext, "mercyblitz-user");
        // 2. 非命名 Bean 的注册方法
//        registerUserBeanDefinition(applicationContext);

        // 启动 Spring 应用上下文
        applicationContext.refresh();
        // 按照类型依赖查找
        System.out.println("Config 类型的所有 Beans" + applicationContext.getBeansOfType(Config.class));
        System.out.println("User 类型的所有 Beans" + applicationContext.getBeansOfType(User.class));
        System.out.println("bean: " + applicationContext.getBean(User.class));
        System.out.println("bean: " + applicationContext.getBean(Config.class));
        // 显示地关闭 Spring 应用上下文
        applicationContext.close();
    }

    public static void registerUserBeanDefinition(BeanDefinitionRegistry registry, String beanName) {
        BeanDefinitionBuilder beanDefinitionBuilder = genericBeanDefinition(User.class);
        beanDefinitionBuilder
                .addPropertyValue("id", 1L)
                .addPropertyValue("name", "小马哥");

        // 判断如果 beanName 参数存在时
        if (StringUtils.hasText(beanName)) {
            // 注册 BeanDefinition
            registry.registerBeanDefinition(beanName, beanDefinitionBuilder.getBeanDefinition());
        } else {
            // 非命名 Bean 注册方法
            BeanDefinitionReaderUtils.registerWithGeneratedName(beanDefinitionBuilder.getBeanDefinition(), registry);
        }
    }

    public static void registerUserBeanDefinition(BeanDefinitionRegistry registry) {
        registerUserBeanDefinition(registry, null);
    }

    // 2. 通过 @Component 方式
    @Component // 定义当前类作为 Spring Bean（组件）
    public static class Config {

        // 1. 通过 @Bean 方式定义

        /**
         * 通过 Java 注解的方式，定义了一个 Bean
         */
        @Bean(name = {"user", "xiaomage-user"})
        public User user() {
            User user = new User();
            user.setId(1L);
            user.setName("小马哥");
            return user;
        }
    }


}
```

@Import不会与@Component重复定义

### Java API

#### 配置类

AnnotatedBeanDefinitionReader.register

```java
	public void register(Class<?>... componentClasses) {
		for (Class<?> componentClass : componentClasses) {
			registerBean(componentClass);
		}
	}
```

#### 手动命名

BeanDefinitionRegistry.registerBeanDefinition

```java
registry.registerBeanDefinition(beanName, beanDefinitionBuilder.getBeanDefinition());
```

#### 自动命名

BeanDefinitionReaderUtils.registerWithGeneratedName

```java
BeanDefinitionReaderUtils.registerWithGeneratedName(beanDefinitionBuilder.getBeanDefinition(), registry);
```

### XML

## SingletonBeanRegistry

注册外部单体对象，不是由spring创建，外部创建的对象由spring托管

```java
public static void main(String[] args) throws InterruptedException {
    // 创建 BeanFactory 容器
    AnnotationConfigApplicationContext applicationContext = new AnnotationConfigApplicationContext();
    // 创建一个外部 UserFactory 对象
    UserFactory userFactory = new DefaultUserFactory();
    SingletonBeanRegistry singletonBeanRegistry = applicationContext.getBeanFactory();
    // 注册外部单例对象
    singletonBeanRegistry.registerSingleton("userFactory", userFactory);
    // 启动 Spring 应用上下文
    applicationContext.refresh();

    // 通过依赖查找的方式来获取 UserFactory
    UserFactory userFactoryByLookup = applicationContext.getBean("userFactory", UserFactory.class);
    System.out.println("userFactory  == userFactoryByLookup : " + (userFactory == userFactoryByLookup));

    // 关闭 Spring 应用上下文
    applicationContext.close();
}
```
