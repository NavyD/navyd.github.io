# WSL2 Ubuntu-20.04编译OpenJDK 12

## 依赖项检查

```bash
$ bash configure --help 
Runnable configure script is not present Generating runnable configure script at /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/build/.configure-support/generated-configure.sh  

Autoconf is not found on the PATH, and AUTOCONF is not set.
You need autoconf to be able to generate a runnable configure script.
You might be able to fix this by running 'sudo apt-get install autoconf'.
Error: Cannot find autoconf
```

这里可能要求`sudo apt-get install autoconf`

## 参数配置

```bash
$ bash configure --enable-debug --with-jvm-variants=server
#...
checking for X11/extensions/shape.h... no configure: error: Could not find all X11 headers (shape.h Xrender.h Xrander.h XTest.h Intrinsic.h). You might be able to fix this by running 'sudo apt-get install libx11-dev libxext-dev libxrender-dev libxrandr-dev libxtst-dev libxt-dev'.
configure exiting with result code 1
#...
configure: error: Could not find cups! You might be able to fix this by running 'sudo apt-get install libcups2-dev'.
configure exiting with result code 1
#...
configure: error: Could not find fontconfig! You might be able to fix this by running 'sudo apt-get install libfontconfig1-dev'.
configure exiting with result code 1
#...
configure: error: Could not find alsa! You might be able to fix this by running 'sudo apt-get install libasound2-dev'.
configure exiting with result code 1
```

在安装了上面提示的依赖后，就可以配置成功

```bash
$ bash configure --enable-debug --with-jvm-variants=server
#...
====================================================
A new configuration has been successfully created in
/home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/build/linux-x86_64-server-fastdebug
using configure arguments '--enable-debug --with-jvm-variants=server'.

Configuration summary:
* Debug level:    fastdebug
* HS debug level: fastdebug
* JVM variants:   server
* JVM features:   server: 'aot cds cmsgc compiler1 compiler2 epsilongc g1gc graal jfr jni-check jvmci jvmti management nmt parallelgc serialgc services shenandoahgc vm-structs zgc'
* OpenJDK target: OS: linux, CPU architecture: x86, address length: 64
* Version string: 12-internal+0-adhoc.navyd.jdk12-06222165c35f (12-internal)

Tools summary:
* Boot JDK:       openjdk version "11.0.8" 2020-07-14 OpenJDK Runtime Environment (build 11.0.8+10-post-Ubuntu-0ubuntu120.04) OpenJDK 64-Bit Server VM (build 11.0.8+10-post-Ubuntu-0ubuntu120.04, mixed mode, sharing)  (at /usr/lib/jvm/java-11-openjdk-amd64)
* Toolchain:      gcc (GNU Compiler Collection)
* C Compiler:     Version 9.3.0 (at /usr/bin/gcc)
* C++ Compiler:   Version 9.3.0 (at /usr/bin/g++)

Build performance summary:
* Cores to use:   9
* Memory limit:   9962 MB
```

## make images

```bash
$ make images
#...
ERROR: Build failed for target 'images' in configuration 'linux-x86_64-server-fastdebug' (exit code 2)
Stopping sjavac server

=== Output from failing command(s) repeated here ===
* For target hotspot_variant-server_libjvm_objs_arguments.o:
In file included from /usr/include/string.h:495,
                 from /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/src/hotspot/share/utilities/globalDefinitions_gcc.hpp:35,
                 from /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/src/hotspot/share/utilities/globalDefinitions.hpp:32,
                 from /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/src/hotspot/share/utilities/align.hpp:28,
                 from /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/src/hotspot/share/runtime/globals.hpp:29,
                 from /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/src/hotspot/share/memory/allocation.hpp:28,
                 from /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/src/hotspot/share/classfile/classLoaderData.hpp:28,
                 from /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/src/hotspot/share/precompiled/precompiled.hpp:34:
In function ‘char* strncpy(char*, const char*, size_t)’,
    inlined from ‘static jint Arguments::parse_each_vm_init_arg(const JavaVMInitArgs*, bool*, JVMFlag::Flags)’ at /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/src/hotspot/share/runtime/arguments.cpp:2472:29:
/usr/include/x86_64-linux-gnu/bits/string_fortified.h:106:34: error: ‘char* __builtin_strncpy(char*, const char*, long unsigned int)’ output truncated before terminating nul copying as many bytes from a string as its length [-Werror=stringop-truncation]
  106 |   return __builtin___strncpy_chk (__dest, __src, __len, __bos (__dest));
   ... (rest of output omitted)

* All command lines available in /home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/build/linux-x86_64-server-fastdebug/make-support/failure-logs.
=== End of repeated output ===

No indication of failed target found.
Hint: Try searching the build log for '] Error'.
Hint: See doc/building.html#troubleshooting for assistance.

make[1]: *** [/home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/make/Init.gmk:310: main] Error 2
make: *** [/home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/make/Init.gmk:186: images] Error 2
```

可以看到build failed，google找了下没什么发现，但是在`doc/building.html#Native Compiler (Toolchain) Requirements`有句话：

 > It should be possible to compile the JDK with both older and newer versions, but the closer you stay to this list, the more likely you are to compile successfully without issues.

| Operating system | Toolchain version                                       |
| ---------------- | ------------------------------------------------------- |
| Linux            | gcc 7.3.0                                               |
| macOS            | Apple Xcode 9.4 (using clang 9.1.0)                     |
| Solaris          | Oracle Solaris Studio 12.4 (with compiler version 5.13) |
| Windows          | Microsoft Visual Studio 2017 update 15.5.5              |

很可能是gcc版本不对引起的，之前`bash configure ...`成功时的gcc版本是9.3.0，尝试用gcc-7

在build failed后，应该make clean

```bash
$ make clean && make dist-clean
#...
Finished building target 'clean' in configuration 'linux-x86_64-server-fastdebug'
#...
Finished building target 'dist-clean' in configuration 'linux-x86_64-server-fastdebug'
```

### 安装gcc-7

```bash
$ sudo add-apt-repository ppa:ubuntu-toolchain-r/test
$ sudo apt-get update 
$ sudo apt-get install gcc-7
$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 100
$ gcc --version
gcc (Ubuntu 7.5.0-6ubuntu2) 7.5.0
```

再尝试`bash configure ...`时提示gcc与g++版本不一致

```bash
$ bash configure --enable-debug --with-jvm-variants=server
#...
====================================================
A new configuration has been successfully created in
/home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/build/linux-x86_64-server-fastdebug
using configure arguments '--enable-debug --with-jvm-variants=server'.

Configuration summary:
* Debug level:    fastdebug
* HS debug level: fastdebug
* JVM variants:   server
* JVM features:   server: 'aot cds cmsgc compiler1 compiler2 epsilongc g1gc graal jfr jni-check jvmci jvmti management nmt parallelgc serialgc services shenandoahgc vm-structs zgc'
* OpenJDK target: OS: linux, CPU architecture: x86, address length: 64
* Version string: 12-internal+0-adhoc.navyd.jdk12-06222165c35f (12-internal)

Tools summary:
* Boot JDK:       openjdk version "11.0.8" 2020-07-14 OpenJDK Runtime Environment (build 11.0.8+10-post-Ubuntu-0ubuntu120.04) OpenJDK 64-Bit Server VM (build 11.0.8+10-post-Ubuntu-0ubuntu120.04, mixed mode, sharing)  (at /usr/lib/jvm/java-11-openjdk-amd64)
* Toolchain:      gcc (GNU Compiler Collection)
* C Compiler:     Version 7.5.0 (at /usr/bin/gcc)
* C++ Compiler:   Version 9.3.0 (at /usr/bin/g++)

Build performance summary:
* Cores to use:   9
* Memory limit:   9962 MB

The following warnings were produced. Repeated here for convenience:
WARNING: C and C++ compiler have different version numbers, 7.5.0 vs 9.3.0.
WARNING: This typically indicates a broken setup, and is not supported
WARNING: C and C++ compiler have different version numbers, 7.5.0 vs 9.3.0.
WARNING: This typically indicates a broken setup, and is not supported

$ g++ --version
g++ (Ubuntu 9.3.0-10ubuntu2) 9.3.0
```

需要安装g++-7

### 安装g++-7

```bash
$ sudo apt-get install g++-7
$ sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 100
$ g++ --version
g++ (Ubuntu 7.5.0-6ubuntu2) 7.5.0
```

### 编译

安装后可正常编译

```bash
$ bash configure --enable-debug --with-jvm-variants=server
#...
====================================================
A new configuration has been successfully created in
/home/navyd/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f/build/linux-x86_64-server-fastdebug
using configure arguments '--enable-debug --with-jvm-variants=server'.

Configuration summary:
* Debug level:    fastdebug
* HS debug level: fastdebug
* JVM variants:   server
* JVM features:   server: 'aot cds cmsgc compiler1 compiler2 epsilongc g1gc graal jfr jni-check jvmci jvmti management nmt parallelgc serialgc services shenandoahgc vm-structs zgc'
* OpenJDK target: OS: linux, CPU architecture: x86, address length: 64
* Version string: 12-internal+0-adhoc.navyd.jdk12-06222165c35f (12-internal)

Tools summary:
* Boot JDK:       openjdk version "11.0.8" 2020-07-14 OpenJDK Runtime Environment (build 11.0.8+10-post-Ubuntu-0ubuntu120.04) OpenJDK 64-Bit Server VM (build 11.0.8+10-post-Ubuntu-0ubuntu120.04, mixed mode, sharing)  (at /usr/lib/jvm/java-11-openjdk-amd64)
* Toolchain:      gcc (GNU Compiler Collection)
* C Compiler:     Version 7.5.0 (at /usr/bin/gcc)
* C++ Compiler:   Version 7.5.0 (at /usr/bin/g++)

Build performance summary:
* Cores to use:   9
* Memory limit:   9962 MB

$ make images
#...
Creating images/jmods/java.base.jmod
Creating jdk image
Creating CDS archive for jdk image
Stopping sjavac server
Finished building target 'images' in configuration 'linux-x86_64-server-fastdebug'
```

## 检查

```bash
# ~/Workspaces/third-party-projects/jdk12-sources/jdk12-06222165c35f
$ ./build/linux-x86_64-server-fastdebug/jdk/bin/java --version
openjdk 12-internal 2019-03-19
OpenJDK Runtime Environment (fastdebug build 12-internal+0-adhoc.navyd.jdk12-06222165c35f)
OpenJDK 64-Bit Server VM (fastdebug build 12-internal+0-adhoc.navyd.jdk12-06222165c35f, mixed mode)
```

编译成功！

## 参考

- [Installing g++ on windows subsystem for linux](https://stackoverflow.com/questions/50729550/installing-g-on-windows-subsystem-for-linux)
- [ubuntu16.04 安装gcc 7.3.0](https://blog.csdn.net/weixin_35762621/article/details/80336291)
- [深入理解Java虚拟机：JVM高级特性与最佳实践（第3版）]
