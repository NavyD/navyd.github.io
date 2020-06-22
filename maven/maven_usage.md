# Maven

## 简介

Maven试图将模式应用于项目的构建基础架构，以便通过提供使用最佳实践的清晰路径来提高理解力和生产力。 Maven本质上是一个项目管理和理解工具，因此提供了一种帮助管理的方法：

- Builds
- Documentation
- Reporting
- Dependencies
- SCMs
- Releases
- Distribution

## Archetype

一个原型(Archetype)被定义为一种原始模式或模型，其他所有同类事物都是从该原始模式或模型中作出的。在Maven中，原型是一个项目的模板，它与一些用户输入相结合，生成一个适合用户需求的工作Maven项目。

这个名字适合我们试图提供一个系统，提供一个生成Maven项目的一致手段。 Archetype将帮助作者为用户创建Maven项目模板，并为用户提供生成这些项目模板的参数化版本的方法。

## 标准目录结构

[Standard Directory Layout](https://maven.apache.org/guides/introduction/introduction-to-the-standard-directory-layout.html#)



## 构建项目

Creating a project from an archetype involves three steps:

- prepare repository reference
- the selection of the archetype,
- the configuration of that archetype,
- the effective creation of the project from the collected information

### 创建新项目

通常需要连接到maven远程仓库来访问库repository。

如果存储库未被管理，并且您想直接引用它，则必须将存储库添加到settings.xml中

- 在当前工作目录调用`mvn archetype:generate`将开始创建项目

```bash
$ mvn archetype:generate
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] Building Maven Stub Project (No POM) 1
[INFO] ------------------------------------------------------------------------
[INFO] 
[INFO] >>> maven-archetype-plugin:3.0.1:generate (default-cli) > generate-sources @ standalone-pom >>>
[INFO] 
[INFO] <<< maven-archetype-plugin:3.0.1:generate (default-cli) < generate-sources @ standalone-pom <<<
[INFO] 
[INFO] 
[INFO] --- maven-archetype-plugin:3.0.1:generate (default-cli) @ standalone-pom ---
...
```

- 首先要求从remote中选择原型。只需输入原型的编号。

下面是输出信息

```bash
$ mvn archetype:generate
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] Building Maven Stub Project (No POM) 1
[INFO] ------------------------------------------------------------------------
[INFO] 
[INFO] >>> maven-archetype-plugin:3.0.1:generate (default-cli) > generate-sources @ standalone-pom >>>
[INFO] 
[INFO] <<< maven-archetype-plugin:3.0.1:generate (default-cli) < generate-sources @ standalone-pom <<<
[INFO] 
[INFO] 
[INFO] --- maven-archetype-plugin:3.0.1:generate (default-cli) @ standalone-pom ---
[INFO] Generating project in Interactive mode
[INFO] No archetype defined. Using maven-archetype-quickstart (org.apache.maven.archetypes:maven-archetype-quickstart:1.0)
Choose archetype:
1: remote -> am.ik.archetype:maven-reactjs-blank-archetype (Blank Project for React.js)
2: remote -> am.ik.archetype:msgpack-rpc-jersey-blank-archetype (Blank Project for Spring Boot + Jersey)
3: remote -> am.ik.archetype:mvc-1.0-blank-archetype (MVC 1.0 Blank Project)
4: remote -> am.ik.archetype:spring-boot-blank-archetype (Blank Project for Spring Boot)
...
1152: remote -> org.apache.maven.archetypes:maven-archetype-profiles (-)
1153: remote -> org.apache.maven.archetypes:maven-archetype-quickstart (An archetype which contains a sample Maven project.)
...
2107: remote -> us.fatehi:schemacrawler-archetype-maven-project (-)
2108: remote -> us.fatehi:schemacrawler-archetype-plugin-command (-)
2109: remote -> us.fatehi:schemacrawler-archetype-plugin-dbconnector (-)
2110: remote -> us.fatehi:schemacrawler-archetype-plugin-lint (-)
2111: remote -> xyz.luan.generator:xyz-generator (-)
Choose a number or apply filter (format: [groupId:]artifactId, case sensitive contains): 1153: 
```

注意：默认的1153表示为`org.apache.maven.archetypes:maven-archetype-quickstart (An archetype which contains a sample Maven project.)`，maven的快速原型

- 输入maven-archetype-quickstart version

```bash
Choose a number or apply filter (format: [groupId:]artifactId, case sensitive contains): 1153:     
Choose org.apache.maven.archetypes:maven-archetype-quickstart version: 
1: 1.0-alpha-1
2: 1.0-alpha-2
3: 1.0-alpha-3
4: 1.0-alpha-4
5: 1.0
6: 1.1
Choose a number: 6: 
```

默认选择的是`maven-archetype-quickstart`的最新版本

- 输入新建项目的`groupId`,`artifactId`,`version`和项目的package

```bash
Choose a number: 6:
Define value for property 'groupId': cn.navyd
Define value for property 'artifactId': MyDemo
Define value for property 'version' 1.0-SNAPSHOT: : 0.0-SNAPSHOT
Define value for property 'package' cn.navyd: : cn.navyd.mydemo
Confirm properties configuration:
groupId: cn.navyd
artifactId: MyDemo
version: 0.0-SNAPSHOT
package: cn.navyd.mydemo
 Y: : y
```

- 项目创建完成

```bash
 Y: : y
[INFO] ----------------------------------------------------------------------------
[INFO] Using following parameters for creating project from Old (1.x) Archetype: maven-archetype-quickstart:1.1
[INFO] ----------------------------------------------------------------------------
[INFO] Parameter: basedir, Value: /home/navyd
[INFO] Parameter: package, Value: cn.navyd.mydemo
[INFO] Parameter: groupId, Value: cn.navyd
[INFO] Parameter: artifactId, Value: MyDemo
[INFO] Parameter: packageName, Value: cn.navyd.mydemo
[INFO] Parameter: version, Value: 0.0-SNAPSHOT
[INFO] project created from Old (1.x) Archetype in dir: /home/navyd/MyDemo
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 12:52 min
[INFO] Finished at: 2018-03-15T16:49:23+08:00
[INFO] Final Memory: 17M/199M
[INFO] ------------------------------------------------------------------------
navyd@navyd-notebook:~$
```

验证项目创建的结果

```bash
$ tree MyDemo/
MyDemo/
├── pom.xml
└── src
    ├── main
    │   └── java
    │       └── cn
    │           └── navyd
    │               └── mydemo
    │                   └── App.java
    └── test
        └── java
            └── cn
                └── navyd
                    └── mydemo
                        └── AppTest.java

11 directories, 3 files
```

### 创建到存在的项目

Creating an archetype from an existing project involves three steps:

- the archetype resolution
- the archetype installation:deployment
- the archetype usage

已存在的项目下可能需要maven必须的pom.xml文件

在maven项目中应该包含pom.xml即Project Object Model (POM)信息

[Advanced Usage](https://maven.apache.org/archetype/maven-archetype-plugin/advanced-usage.html#)

注意：

- 如果已存在的项目目录不符合maven标准的目录结构将会报错

```bash
~/Workspace/eclipse/workspace/JavaNio$ mvn archetype:create-from-project
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] Building Maven Stub Project (No POM) 1
[INFO] ------------------------------------------------------------------------
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 0.333 s
[INFO] Finished at: 2018-03-15T17:27:00+08:00
[INFO] Final Memory: 9M/150M
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-archetype-plugin:3.0.1:create-from-project (default-cli): Goal requires a project to execute but there is no POM in this directory (/home/navyd/Workspace/eclipse/workspace/JavaNio). Please verify you invoked Maven from the correct directory. -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MissingProjectException
```







### 过滤Archetype

在选择原型(Archetype)时存在过多选项的问题，maven允许指定groupid和artifactid过滤list

- 在创建命令上指定

```bash
$ mvn archetype:generate -Dfilter=org.apache:struts
```

- 在选择是指定`[groupId:]artifactId`来过滤掉不需要的原型

```bash
$ mvn archetype:generate
[INFO] Scanning for projects...
...
Choose a number or apply filter (format: [groupId:]artifactId, case sensitive contains): : org.apache:struts
Choose archetype:
1: remote -> org.apache.struts:struts2-archetype-angularjs (-)
2: remote -> org.apache.struts:struts2-archetype-blank (-)
3: remote -> org.apache.struts:struts2-archetype-convention (-)
4: remote -> org.apache.struts:struts2-archetype-dbportlet (-)
5: remote -> org.apache.struts:struts2-archetype-plugin (-)
6: remote -> org.apache.struts:struts2-archetype-portlet (-)
7: remote -> org.apache.struts:struts2-archetype-starter (-)
Choose a number or apply filter (format: [groupId:]artifactId, case sensitive contains): : 7
Choose org.apache.struts:struts2-archetype-starter version: 
```

### 编译

切换到由`mvn archetype:generate`创建的pom.xml的目录，并执行以下命令以编译应用程序源代码：

```bash
$ mvn compile
```

maven将编译后的目标文件放在`${basedir}/target/classes`

注意：首次编译该项目可能需要时间下载需要的插件和关联依赖。

### 编译并执行测试类

```bash
$ mvn test
```

注意：

- 如果需要maven可能需要下载测试类需要的依赖和插件
- 在编译和运行测试类前需要编译main的代码，如果该代码不是最新的

#### 仅编译测试类

```bash
$ mvn test-compile
```

### 打包

制作JAR文件非常简单，可以通过执行以下命令来完成：

```bash
$ mvn package
```

在POM中的packaging元素被设置为jar，maven将其打包为jar文件，如果设置为其他类型，将打包为该类型。

打包文件在目录：`${basedir}/target`

### 安装打包项目到本地仓库

maven允许将已打包项目安装到本地仓库`${user.home}/.m2/repository`

```bash
$ mvn install
```

仓库介绍：[Introduction to Repositories](https://maven.apache.org/guides/introduction/introduction-to-repositories.html)

请注意，surefire插件（执行测试）使用特定的命名约定查找包含在文件中的测试。默认情况下，测试包括：

- `**/*Test.java`
- `**/Test*.java`
- `**/*TestCase.java`

And the default excludes are:

- `**/Abstract*Test.java`
- `**/Abstract*TestCase.java`

### 移除构建数据

在启动之前删除具有所有构建数据的target目录

```bash
$ mvn clean
```

注意：

- 该命令需要在对应maven项目的目录下执行，否则将报错

```bash
~/Desktop$ mvn clean
[INFO] Scanning for projects...
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 0.115 s
[INFO] Finished at: 2018-03-15T21:39:47+08:00
[INFO] Final Memory: 5M/119M
[INFO] ------------------------------------------------------------------------
[ERROR] The goal you specified requires a project to execute but there is no POM in this directory (/home/navyd/Desktop). Please verify you invoked Maven from the correct directory. -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MissingProjectException
```



## 配置

所有配置说明：[full reference](https://maven.apache.org/maven-settings/settings.html)

配置向导：[Configuring Maven](https://maven.apache.org/guides/mini/guide-configuring-maven.html#)

### 下载jar源码和文档

在maven的本地文件夹中`~/.m2/setting.xml`添加如下代码：

```xml
<settings>

   <!-- ... other settings here ... -->

    <profiles>
        <profile>
            <id>downloadSources</id>
            <properties>
                <downloadSources>true</downloadSources>
                <downloadJavadocs>true</downloadJavadocs>
            </properties>
        </profile>
    </profiles>

    <activeProfiles>
        <activeProfile>downloadSources</activeProfile>
    </activeProfiles>
</settings>
```

参考：

[Maven – Always download sources and javadocs](https://stackoverflow.com/questions/5780758/maven-always-download-sources-and-javadocs)

[dependency:sources](https://maven.apache.org/plugins/maven-dependency-plugin/sources-mojo.html)

### 配置编译版本

maven默认的编译版本为java 1.5，创建的项目导入的jre包为jre 1.5，导致高版本无法通过编译

可以在项目的pom.xml中编辑：

- 配置插件参数

```xml
<project>
  [...]
  <properties>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
  </properties>
  [...]
</project>
```

- 直接配置compiler插件

```xml
<project>
  [...]
  <build>
    [...]
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.7.0</version>
        <configuration>
          <source>1.8</source>
          <target>1.8</target>
        </configuration>
      </plugin>
    </plugins>
    [...]
  </build>
  [...]
</project>
```

在更改pom.xml后应该更新项目编译:（未测试）

```
mvn clean && mvn compiler
```

### 配置指定compile encoding

windows平台编译时可能会遇到`unmappable character (0x80) for encoding GBK`的问题：

```shell
PS C:\Users\navyd\Workspaces\projects\LightWebServer> mvn compile
[INFO] Scanning for projects...
[INFO]
[INFO] -----------------< com.lightwebserver:lightwebserver >------------------
[INFO] Building lightwebserver 1.0-SNAPSHOT
[INFO] --------------------------------[ jar ]---------------------------------
[INFO]
[INFO] --- maven-resources-plugin:2.6:resources (default-resources) @ lightwebserver ---
[WARNING] Using platform encoding (GBK actually) to copy filtered resources, i.e. build is platform dependent!
[INFO] Copying 7 resources
[INFO]
[INFO] --- maven-compiler-plugin:3.6.0:compile (default-compile) @ lightwebserver ---
[INFO] Changes detected - recompiling the module!
[WARNING] File encoding has not been set, using platform encoding GBK, i.e. build is platform dependent!
[INFO] Compiling 39 source files to C:\Users\navyd\Workspaces\projects\LightWebServer\target\classes
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/util/ReflectUtil.java:[24,108] unmappable character (0x80) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/http/RequestHandler.java:[75,31] unmappable character (0xAD) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/util/FileUtil.java:[16,28] unmappable character (0xA6) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/util/FileUtil.java:[18,26] unmappable character (0x84) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/util/FileUtil.java:[19,26] unmappable character (0x84) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerScan.java:[37,60] unmappable character (0xBA) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerScan.java:[73,68] unmappable character (0xBA) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/io/Server.java:[30,15] unmappable character (0xA8) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/io/Server.java:[36,15] unmappable character (0x96) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/io/Server.java:[45,44] unmappable character (0xAF) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/io/Server.java:[53,26] unmappable character (0xA8) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/io/Server.java:[83,12] unmappable character (0x80) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/io/Server.java:[93,62] unmappable character (0xBD) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/io/Server.java:[94,43] unmappable character (0x80) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerMethod.java:[48,57] unmappable character (0x80) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerMethod.java:[80,10] unmappable character (0x80) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerMethod.java:[80,15] unmappable character (0x80) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerMethod.java:[81,27] unmappable character (0x8B) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerMethod.java:[89,57] unmappable character (0xA1) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerMethod.java:[97,101] unmappable character (0x80) for encoding GBK
[ERROR] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerMethod.java:[105,71] unmappable character (0xBC) for encoding GBK
[INFO] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerScan.java: Some input files use or override a deprecated API.
[INFO] /C:/Users/navyd/Workspaces/projects/LightWebServer/src/main/java/com/light/mvc/ControllerScan.java: Recompile with -Xlint:deprecation for details.
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  2.928 s
[INFO] Finished at: 2020-06-22T11:01:12+08:00
[INFO] ------------------------------------------------------------------------
```

此时项目的配置是

```xml
        <plugins>
            <plugin> <!-- 编译 -->
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.6.0</version>
                <configuration>
                    <source>1.8</source>
                    <target>1.8</target>
                </configuration>
            </plugin>
        </plugins>
```

未指定maven编译plugin的encoding字符集：utf-8，修改后可正常compile

```xml
        <plugins>
            <plugin> <!-- 编译 -->
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.6.0</version>
                <configuration>
                    <source>1.8</source>
                    <target>1.8</target>
                    <!-- utf8编译 -->
                    <encoding>UTF-8</encoding>
                </configuration>
            </plugin>
        </plugins>
```

参考：[Compile Using -source and -target javac Options](https://maven.apache.org/plugins/maven-compiler-plugin/examples/set-compiler-source-and-target.html#)

## 插件

与依赖dependency很像

下面是在pom.xml文件中配置使用java 1.5编译项目

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <version>3.3</version>
      <configuration>
        <source>1.5</source>
        <target>1.5</target>
      </configuration>
    </plugin>
  </plugins>
</build>
```

注意：

- 如果该插件不包含在本地仓库，将会下载并使用指定版本的插件（如果不指定版本，将默认下载最新版本）
- configuration将指定参数应用到插件中

## 生命周期

Maven基于构建生命周期的核心概念。这意味着建立和分配特定工件（项目）的过程已经明确定义。

有三种内置的构建生命周期：

- default：用于项目部署
- clean：用于清理项目
- site：用于项目站点文档的创建

每种生命周期都由多种阶段组成

default主要包括：

- `validate` - validate the project is correct and all necessary information is available
- `compile` - compile the source code of the project
- `test` - test the compiled source code using a suitable unit testing framework. These tests should not require the code be packaged or deployed
- `package` - take the compiled code and package it in its distributable format, such as a JAR.
- `verify` - run any checks on results of integration tests to ensure quality criteria are met
- `install` - install the package into the local repository, for use as a dependency in other projects locally
- `deploy` - done in the build environment, copies the final package to the remote repository for sharing with other developers and projects.

maven将按照指定的顺序完成生命周期。每个阶段都会验证之前的阶段是否完成，如果没有就执行。如`mvn install`将完成`validate`, `compile`, `package`, 等等，

如果存在子项目，maven将遍历每一个子项目并完成相应的生命周期命令。

### 阶段插件目标

构建阶段负责构建生命周期中的特定步骤，履行这些责任步骤的方式可能会有所不同。这是由于通过声明插件目标绑定到这些构建阶段来完成的。

插件目标表示比构建阶段更小的任务，用于构建和管理项目

插件目标可以绑定0到多个构建阶段，不受任何构建阶段限制的目标可以通过直接调用在构建生命周期之外执行。执行顺序取决于调用目标和构建阶段的顺序。

如下面在clean和package构建阶段中指定了`dependency:copy-dependencies`插件目标

```bash
mvn clean dependency:copy-dependencies package
```

该命令首先执行clean生命周期前的阶段，然后执行阶段目标dependency:copy-dependencies，最后执行default生命周期package前的阶段。



如果一个目标绑定到一个或多个构建阶段，那么将在所有这些阶段中调用该目标。

一个构建阶段可以绑定0到多个目标。如果该构建阶段没有绑定目标则不会执行该构建阶段，否则将执行所有绑定的目标

### 在项目中构建生命周期

#### 使用packaging

在POM中的元素`packaging`指定了一些合法值：`jar`, `war`, `ear` and `pom`，默认为jar

每个packaging都包含特定的阶段如下面表示jar的构建阶段和阶段目标：

| `process-resources`      | `resources:resources`     |
| ------------------------ | ------------------------- |
| `compile`                | `compiler:compile`        |
| `process-test-resources` | `resources:testResources` |
| `test-compile`           | `compiler:testCompile`    |
| `test`                   | `surefire:test`           |
| `package`                | `jar:jar`                 |
| `install`                | `install:install`         |
| `deploy`                 | `deploy:deploy`           |

不同的packaging可能需要不同的处理例如，纯粹为元数据的项目（包装值为pom）仅将目标绑定到安装和部署阶段

请注意，对于某些可用的包装类型，您可能还需要在POM的部分中包含特定的插件，并为该插件指定 true 。一个需要这个插件的例子是Plexus插件，它提供了一个丛应用程序和丛服务包装。

#### 配置插件

为阶段添加目标的第二种方法是在您的项目中配置插件。插件是为Maven提供目标的工件。此外，插件可能有一个或多个目标，其中每个目标代表该插件的功能。例如，Compiler插件有两个目标：compile和testcompile。前者编译主代码的源代码，后者编译测试代码的源代码

插件可以包含指示将目标绑定到哪个生命周期阶段的信息。请注意，单独添加插件并不足以提供信息 - 您还必须指定要作为构建的一部分运行的目标。

已配置的目标将被添加到已选定包装的已生效周期的目标中。如果多个目标绑定到一个阶段中，所使用的顺序是那些从packaging中被执行的。其次是在POM中配置的那些。请注意，您可以使用<executions>元素来更好地控制特定目标的顺序。如果需要的话，您可以多次使用不同的配置来运行同一个目标



当多个执行被给定一个特定的阶段时，它们按照POM中指定的顺序执行，首先是继承的执行。

一些目标可以在一个以上的阶段中使用，并且可能没有明智的默认，你可以指定一个阶段