---
title: "Import in Spring"
date: 2022-03-18T21:47:54+08:00
draft: true
tags: [java, spring]
---

对于[spring @Import](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Import.html)文档中提到

> Indicates one or more component classes to import — typically @Configuration classes.
> ...
> Allows for importing @Configuration classes, ImportSelector and ImportBeanDefinitionRegistrar implementations, as well as regular component classes

`@Import` 注解用来帮助我们把一些需要定义为 Bean 的类导入到IOC容器里面。下面我们就对 `@Import` 注解的使用做一个简单的总结。

## `@Import` 引入普通类

`@Import` 引入普通的类可以帮助我们把普通的类定义为 Bean。`@Import` 可以添加在`@SpringBootApplication` (启动类)、`@Configuration` (配置类)、`@Component` (组件类) 对应的类上。

```java
@SpringBootApplication
@Import(ImportBean.class) // 通过@Import注解把ImportBean添加到IOC容器里面去
public class MyBatisApplication {

    public static void main(String[] args) {
        SpringApplication.run(MyBatisApplication.class, args);
    }

}
```

## `@Import` 引入配置类 (@Configuration 修饰的类)

`@Import` 还可以引入一个 `@Configuration` 修饰的类 (引入配置类)，从而把让配置类生效 (配置类下的所有 Bean 添加到 IOC 容器里面去)。在自定义 starter 的时候经常会用到。

如果配置类在标准的 SpringBoot 包结构下 (SpringBootApplication 启动类包的根目录下)。是不需要 `@Import` 导入配置类的，SpringBoot 自动帮做了。上面的情况一般用于 `@Configuration` 配置类不在标准的 SpringBoot 包结构下面。所以一般在自定义 starter 的时候用到

```java
@Configuration(proxyBeanMethods = false)
@Import({  // import了两个哈
        XXXDataConfiguration.XXXPartOneConfiguration.class,
        XXXDataConfiguration.XXXPartTwoConfiguration.class
})
public class XXXDataAutoConfiguration {
}


public class XXXDataConfiguration {

    @Configuration(proxyBeanMethods = false)
    static class XXXPartOneConfiguration {

        @Bean
        @ConditionalOnMissingBean
        public BeanForIoc beanForIoc() {
            return new BeanForIoc();
        }

    }

    @Configuration(proxyBeanMethods = false)
    static class XXXPartTwoConfiguration {

        /**
         * 省略了@Bean的使用
         */

    }

}
```

## `@Import` 引入 ImportSelector 的实现类

`@Import` 还可以引入 ImportSelector 的实现类，把 ImportSelector 接口 selectImports () 方法返回的 Class 名称都定义为 bean。注意 selectImports () 方法的参数 AnnotationMetadata，通过这个参数我们可以获取到 `@Import` 标注的 Class 的各种信息。这一点特别有用，用于做一些参数的传递。在 SpringBoot 的自动化配置和 @EnableXXX (功能性注解) 都有它的存在。

```java
public interface ImportSelector {

    /**
     * 用于指定需要注册为bean的Class名称
     * 当在@Configuration标注的Class上使用@Import引入了一个ImportSelector实现类后，会把实现类中返回的Class名称都定义为bean。
     *
     * 通过其参数AnnotationMetadata importingClassMetadata可以获取到@Import标注的Class的各种信息，
     * 包括其Class名称，实现的接口名称、父类名称、添加的其它注解等信息，通过这些额外的信息可以辅助我们选择需要定义为Spring bean的Class名称
     */
    String[] selectImports(AnnotationMetadata importingClassMetadata);

}
```

关于 `@Import` 引入 ImportSelector 的实现类的使用，我们举几个简单的使用场景 (实际开发肯定比这复杂的多的)。

### 静态 import 场景 (注入已知的类)

静态场景 (注入已知的类)，很简单通过实现 ImportSelector 类把我们需要定义为 bean 的类直接返回就好， 比如下面的例子。我们来一个 EnableXXX 的注解，通过 XXXConfigurationSelector 注入一个已知的类 XXX。

```java
/**
 * XXXConfigurationSelector一定要配合@Import使用
 */
public class XXXConfigurationSelector implements ImportSelector {
    @Override
    @NonNull
    public String[] selectImports(@NonNull AnnotationMetadata importingClassMetadata) {
        // 把XXX对应的类，定义为Bean
        return new String[]{XXX.class.getName()};
    }
}

/**
 * 注意 @Import(XXXConfigurationSelector.class)
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Import(XXXConfigurationSelector.class)
public @interface EnableXXX {
}

@SpringBootApplication
@EnableXXX // 使之生效
public class MyBatisApplication {

    public static void main(String[] args) {
        SpringApplication.run(MyBatisApplication.class, args);
    }

}
```

### 2.2 动态 import 场景 (注入指定条件的类)

我们做一个这样的功能，我们需要把指定包路径下所有实现了 HelloService 接口的类做为 bean 添加到 IOC 容器里面去。@ComponentScan 注解用来帮我们指定路径。具体实现如下：

```java
public interface HelloService {

    void function();

}

public class DynamicSelectImport implements ImportSelector {
    /**
     * DynamicSelectImport需要配合@Import()注解使用
     * <p>
     * 通过其参数AnnotationMetadata importingClassMetadata可以获取到@Import标注的Class的各种信息，
     * 包括其Class名称，实现的接口名称、父类名称、添加的其它注解等信息，通过这些额外的信息可以辅助我们选择需要定义为Spring bean的Class名称
     */
    @Override
    public String[] selectImports(AnnotationMetadata importingClassMetadata) {
        // 第一步：获取到通过ComponentScan指定的包路径
        String[] basePackages = null;
        // @Import注解对应的类上的ComponentScan注解
        if (importingClassMetadata.hasAnnotation(ComponentScan.class.getName())) {
            Map<String, Object> annotationAttributes = importingClassMetadata.getAnnotationAttributes(ComponentScan.class.getName());
            basePackages = (String[]) annotationAttributes.get("basePackages");
        }
        if (basePackages == null || basePackages.length == 0) {
            //ComponentScan的basePackages默认为空数组
            String basePackage = null;
            try {
                // @Import注解对应的类的包名
                basePackage = Class.forName(importingClassMetadata.getClassName()).getPackage().getName();
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            }
            basePackages = new String[]{basePackage};
        }
        // 第er步，知道指定包路径下所有实现了HelloService接口的类（ClassPathScanningCandidateComponentProvider的使用）
        ClassPathScanningCandidateComponentProvider scanner = new ClassPathScanningCandidateComponentProvider(false);
        TypeFilter helloServiceFilter = new AssignableTypeFilter(HelloService.class);
        scanner.addIncludeFilter(helloServiceFilter);
        Set<String> classes = new HashSet<>();
        for (String basePackage : basePackages) {
            scanner.findCandidateComponents(basePackage).forEach(beanDefinition -> classes.add(beanDefinition.getBeanClassName()));
        }
        // 第三步，返回添加到IOC容器里面去
        return classes.toArray(new String[0]);
    }
}

@Configuration
@ComponentScan("com.tuacy.collect.mybatis") // 指定路径
@Import(DynamicSelectImport.class)
public class DynamicSelectConfig {
}
```

## `@Import` 引入 ImportBeanDefinitionRegistrar 的实现类

`@Import` 引入 ImportBeanDefinitionRegistrar 的实现类。一般用来动态注册 bean。最重要的一点是还可以**对这些 BeanDefinition 进行额外的修改或增强**。咱们经常使用的 mybatis `@MapperScan` 就是用这种方式实现的。

```java
/**
 * ImportBeanDefinitionRegistrar，我们一般会实现ImportBeanDefinitionRegistrar类，然后配合一个自定义的注解一起使用。而且在注解类上@Import我们的这个实现类。
 * 通过自定义注解的配置，拿到注解的一些元数据。然后在ImportBeanDefinitionRegistrar的实现类里面做相应的逻辑处理，比如把自定义注解标记的类添加到Spring IOC容器里面去。
 */
public interface ImportBeanDefinitionRegistrar {

    /**
     * 根据注解的给定注释元数据，根据需要注册bean定义
     * @param importingClassMetadata 可以拿到@Import的这个class的Annotation Metadata
     * @param registry BeanDefinitionRegistry 就可以拿到目前所有注册的BeanDefinition，然后可以对这些BeanDefinition进行额外的修改或增强。
     */
    void registerBeanDefinitions(AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry);

}
```

关于 `@Import` 引入 ImportBeanDefinitionRegistrar 的使用强烈建议大家去看看 mybatis 关于 `@MapperScan` 的处理源码。特别有意思。我们也举一个非常简单的实例，来让大家直观的看到 ImportBeanDefinitionRegistrar 的使用，比如我们想把指定包路径下所有添加了 BeanIoc 注解的类注册为 bean。具体实现如下：

```java
/**
 * 我们会把添加了该注解的类作为bean
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Documented
public @interface BeanIoc {

}

/**
 * 定义包路径。(指定包下所有添加了BeanIoc注解的类作为bean)
 * 注意这里 @Import(BeanIocScannerRegister.class) 的使用
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Documented
@Import(BeanIocScannerRegister.class)
public @interface BeanIocScan {
    String[] basePackages() default "";
}


/**
 * 搜索指定包下所有添加了BeanIoc注解的类，并且把这些类添加到ioc容器里面去
 */
public class BeanIocScannerRegister implements ImportBeanDefinitionRegistrar, ResourceLoaderAware {

    private final static String PACKAGE_NAME_KEY = "basePackages";

    private ResourceLoader resourceLoader;

    @Override
    public void registerBeanDefinitions(AnnotationMetadata annotationMetadata, BeanDefinitionRegistry beanDefinitionRegistry) {
        //1. 从BeanIocScan注解获取到我们要搜索的包路径
        AnnotationAttributes annoAttrs = AnnotationAttributes.fromMap(annotationMetadata.getAnnotationAttributes(BeanIocScan.class.getName()));
        if (annoAttrs == null || annoAttrs.isEmpty()) {
            return;
        }
        String[] basePackages = (String[]) annoAttrs.get(PACKAGE_NAME_KEY);
        // 2. 找到指定包路径下所有添加了BeanIoc注解的类，并且把这些类添加到IOC容器里面去
        ClassPathBeanDefinitionScanner scanner = new ClassPathBeanDefinitionScanner(beanDefinitionRegistry, false);
        scanner.setResourceLoader(resourceLoader);
        scanner.addIncludeFilter(new AnnotationTypeFilter(BeanIoc.class));
        scanner.scan(basePackages);
    }

    @Override
    public void setResourceLoader(ResourceLoader resourceLoader) {
        this.resourceLoader = resourceLoader;
    }
}


/**
 * 使用，使BeanIocScan生效
 */
@Configuration
@BeanIocScan(basePackages = "com.tuacy.collect.mybatis")
public class BeanIocScanConfig {
}
```

参考：

* [SpringBoot 之 @Import 注解正确使用方式](https://blog.csdn.net/wuyuxing24/article/details/105915616)
* [spring api @Import](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Import.html)
* [ImportSelector](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/ImportSelector.html)
* [ImportBeanDefinitionRegistrar](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/ImportBeanDefinitionRegistrar.html)
