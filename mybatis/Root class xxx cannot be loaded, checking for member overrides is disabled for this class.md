# Root class xxx cannot be loaded, checking for member overrides is disabled for this class

## 描述

在maven插件MBG中对entity使用`rootclass`时无法加载对应的class类，使得entity生成了rootclass中存在的属性。generatorConfig.xml对应`javaModelGenerator`部分配置

```xml
<javaModelGenerator targetPackage="xyz.navyd.usercenter.domain.entity.auto" targetProject="src/main/java">
    <property name="enableSubPackages" value="false"/>
    <property name="trimStrings" value="false"/>
    <property name="rootClass" value="xyz.navyd.common.domain.entity.BaseEntity"/>
</javaModelGenerator>
```

```java
package xyz.navyd.common.domain.entity;
@Data
@SuperBuilder
@EqualsAndHashCode(callSuper = true)
@ToString(callSuper = true)
public class UserInfo extends BaseEntity implements Serializable {
    // 生成存在rootclass上的属性
    private Long id;
    private LocalDateTime gmtCreate;
    private LocalDateTime gmtModified;
    private String wxId;
    private String wxNickname;
    private String roles;
    private String avatarUrl;
    private Integer bonus;
    private static final long serialVersionUID = 1L;
}
@Data
@SuperBuilder
@NoArgsConstructor
public class BaseEntity {
    private Long id;
    private LocalDateTime gmtCreate;
    private LocalDateTime gmtModified;
}
```

## 原因

MBG源码中`org.mybatis.generator.codegen.mybatis3.model.BaseRecordGenerator#getCompilationUnits`开始加载rootclass, 最后生成`org.mybatis.generator.codegen.RootClassInfo`时`ObjectFactory.externalClassForName`无法创建root class, 异常后添加信息到warnings list中

在maven pom中配置了对应的`BaseEntity`所在的jar包，在springboot子项目`sharing-common`中的BaseEntity.java打包后还是无法加载，

```xml
<plugin>
    <groupId>org.mybatis.generator</groupId>
    <artifactId>mybatis-generator-maven-plugin</artifactId>
    <dependencies>
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>${mysql.version}</version>
        </dependency>
        <dependency>
            <groupId>xyz.navyd</groupId>
            <artifactId>sharing-common</artifactId>
            <version>${module.sharing-common.version}</version>
        </dependency>
    </dependencies>
    <configuration>
        <!-- 输出详细信息 -->
        <verbose>true</verbose>
        <!-- 覆盖生成文件 -->
        <overwrite>true</overwrite>
        <!-- 定义配置文件 -->
        <!--                    <configurationFile>${basedir}/src/main/resources/generator-configuration.xml</configurationFile>-->
    </configuration>
</plugin>
```

下面是springboot项目使用`spring-boot-maven-plugin`插件打包的部分目录结构

```bash
META-INF/
META-INF/MANIFEST.MF
org/
org/springframework/
org/springframework/boot/
org/springframework/boot/loader/
org/springframework/boot/loader/ClassPathIndexFile
#...
META-INF/maven/xyz.navyd/sharing-common/
BOOT-INF/classes/xyz/navyd/common/domain/entity/BaseEntity$BaseEntityBuilderImpl.class
BOOT-INF/classes/xyz/navyd/common/domain/entity/BaseEntity$BaseEntityBuilder.class
BOOT-INF/classes/xyz/navyd/common/domain/entity/BaseEntity.class
#...
```

下面是用jar命令`jar -cvf BaseEntity.jar xyz/navyd/common/domain/entity`打包结构

```bash
META-INF/
META-INF/MANIFEST.MF
xyz/navyd/common/domain/entity/BaseEntity$BaseEntityBuilder.class
xyz/navyd/common/domain/entity/BaseEntity$BaseEntityBuilderImpl.class
xyz/navyd/common/domain/entity/BaseEntity.class
```

显然spring boot jar包不是标准的jar，可能无法正确被MBG识别

## 解决方案

使用标准jar打包后可由maven配置或MBG generatorConfig.xml配置

### maven

用maven标准插件打包并在`mybatis-generator-maven-plugin`中配置为依赖

### MBG generatorConfig.xml

`classPathEntry`支持jar/zip/classpath

目录结构

```bash
├── BaseEntity.jar
└── xyz
    └── navyd
        ├── SharingCommonApplication.class
        └── common
            ├── dao
            │   ├── BaseMapper.class
            │   └── ExampleMapper.class
            └── domain
                └── entity
                    ├── BaseEntity$BaseEntityBuilder.class
                    ├── BaseEntity$BaseEntityBuilderImpl.class
                    └── BaseEntity.class
```

#### jar

在generatorConfig.xml中配置`classPath`为jar包

```xml
<classPathEntry location="${dir}/BaseEntity.jar"/>
```

#### classpath

直接设置包含class文件路径

```xml
<classPathEntry location="${dir}"/>
```

参考：

- [`The <classPathEntry> Element`](https://mybatis.org/generator/configreference/classPathEntry.html)
