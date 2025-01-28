---
title: "Cron Best Practices"
date: 2022-09-12T12:19:48+08:00
draft: true
tags: [linux, cron]
---

> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [blog.sanctum.geek.nz](https://blog.sanctum.geek.nz/cron-best-practices/)

> The time-based job scheduler cron(8) has been around since Version 7 Unix, and its crontab(5) syntax ......

The time-based job scheduler [`cron(8)`](http://linux.die.net/man/8/cron) has been around since Version 7 Unix, and its [`crontab(5)`](http://linux.die.net/man/1/crontab) syntax is familiar even for people who don’t do much Unix system administration. It’s [standardised](http://pubs.opengroup.org/onlinepubs/7908799/xcu/crontab.html), reasonably flexible, simple to configure, and works reliably, and so it’s trusted by both system packages and users to manage many important tasks.

However, like many older Unix tools, `cron(8)`‘s simplicity has a drawback: it relies upon the user to know some detail of how it works, and to correctly implement any other safety checking behaviour around it. Specifically, all it does is try and run the job at an appropriate time, and email the output. For simple and unimportant per-user jobs, that may be just fine, but for more crucial system tasks it’s worthwhile to wrap a little extra infrastructure around it and the tasks it calls.

There are a few ways to make the way you use `cron(8)` more robust if you’re in a situation where keeping track of the running job is desirable.

Apply the principle of least privilege
--------------------------------------

The sixth column of a system `crontab(5)` file is the username of the user as which the task should run:

```
0 * * * *  root  cron-task
```

To the extent that is practical, you should run the task as a user with only the privileges it needs to run, and nothing else. This can sometimes make it worthwhile to create a dedicated system user purely for running scheduled tasks relevant to your application.

```
0 * * * *  myappcron  cron-task
```

This is not just for security reasons, although those are good ones; it helps protect you against nasties like scripting errors attempting to [remove entire system directories](https://github.com/valvesoftware/steam-for-linux/issues/3671).

Similarly, for tasks with database systems such as MySQL, don’t use the administrative `root` user if you can avoid it; instead, use or even create a dedicated user with a unique random password stored in a locked-down `~/.my.cnf` file, with only the needed permissions. For a MySQL backup task, for example, only a few permissions should be required, including `SELECT`, `SHOW VIEW`, and `LOCK TABLES`.

In some cases, of course, you really will need to be `root`. In particularly sensitive contexts you might even consider using `sudo(8)` with appropriate `NOPASSWD` options, to allow the dedicated user to run only the appropriate tasks as `root`, and nothing else.

Test the tasks
--------------

Before placing a task in a `crontab(5)` file, you should test it on the command line, as the user configured to run the task and with the appropriate environment set. If you’re going to run the task as `root`, use something like `su` or `sudo -i` to get a root shell with the user’s expected environment first:

```
$ sudo -i -u cronuser
$ cron-task
```

Once the task works on the command line, place it in the `crontab(5)` file with the timing settings modified to run the task a few minutes later, and then watch `/var/log/syslog` with `tail -f` to check that the task actually runs without errors, and that the task itself completes properly:

```
May  7 13:30:01 yourhost CRON[20249]: (you) CMD (cron-task)
```

This may seem pedantic at first, but it becomes routine very quickly, and it saves a lot of hassles down the line as it’s very easy to make an assumption about something in your environment that doesn’t actually hold in the one that `cron(8)` will use. It’s also a necessary acid test to make sure that your `crontab(5)` file is well-formed, as some implementations of `cron(8)` will refuse to load the entire file if one of the lines is malformed.

If necessary, you can set arbitrary environment variables for the tasks at the top of the file:

```
MYVAR=myvalue

0 * * * *  you  cron-task
```

Don’t throw away errors or useful output
----------------------------------------

You’ve probably seen tutorials on the web where in order to keep the `crontab(5)` job from sending standard output and/or standard error emails every five minutes, shell redirection operators are included at the end of the job specification to discard both the standard output and standard error. This kluge is particularly common for running web development tasks by automating a request to a URL with [`curl(1)`](https://curl.haxx.se/docs/manpage.html) or [`wget(1)`](http://linux.die.net/man/1/wget):

```
*/5 * * *  root  curl https://example.com/cron.php >/dev/null 2>&1
```

Ignoring the output completely is generally not a good idea, because unless you have other tasks or monitoring ensuring the job does its work, you won’t notice problems (or know what they are), when the job emits output or errors that you actually care about.

In the case of `curl(1)`, there are just way too many things that could go wrong, that you might notice far too late:

*   The script could get broken and return 500 errors.
*   The URL of the `cron.php` task could change, and someone could forget to add a HTTP 301 redirect.
*   Even if a HTTP 301 redirect is added, if you don’t use `-L` or `--location` for `curl(1)`, it won’t follow it.
*   The client could get blacklisted, firewalled, or otherwise impeded by automatic or manual processes that falsely flag the request as spam.
*   If using HTTPS, connectivity could break due to cipher or protocol mismatch.

The author has seen all of the above happen, in some cases very frequently.

As a general policy, it’s worth taking the time to read the manual page of the task you’re calling, and to look for ways to correctly control its output so that it emits only the output you actually want. In the case of `curl(1)`, for example, I’ve found the following formula works well:

```
curl -fLsS -o /dev/null http://example.com/
```

*   `-f`: If the HTTP response code is an error, emit an error message rather than the 404 page.
*   `-L`: If there’s an HTTP 301 redirect given, try to follow it.
*   `-sS`: Don’t show progress meter (`-S` stops `-s` from also blocking error messages).
*   `-o /dev/null`: Send the standard output (the actual page returned) to `/dev/null`.

This way, the `curl(1)` request should stay silent if everything is well, per the old Unix philosophy [Rule of Silence](http://www.linfo.org/rule_of_silence.html).

You may not agree with some of the choices above; you might think it important to e.g. log the complete output of the returned page, or to fail rather than silently accept a 301 redirect, or you might prefer to use `wget(1)`. The point is that you take the time to understand in more depth what the called program will actually emit under what circumstances, and make it match your requirements as closely as possible, rather than blindly discarding all the output and (worse) the errors. Work with [Murphy’s law](https://en.wikipedia.org/wiki/Murphy%27s_law); assume that anything that can go wrong eventually will.

Send the output somewhere useful
--------------------------------

Another common mistake is failing to set a useful `MAILTO` at the top of the `crontab(5)` file, as the specified destination for any output and errors from the tasks. `cron(8)` uses the system mail implementation to send its messages, and typically, default configurations for mail agents will simply send the message to an `mbox` file in `/var/mail/$USER`, that they may not ever read. This defeats much of the point of mailing output and errors.

This is easily dealt with, though; ensure that you can send a message to an address you actually _do_ check from the server, perhaps using `mail(1)`:

```
$ printf '%s\n' 'Test message' | mail -s 'Test subject' you@example.com
```

Once you’ve verified that your mail agent is correctly configured and that the mail arrives in your inbox, set the address in a `MAILTO` variable at the top of your file:

```
MAILTO=you@example.com

0 * * * *    you  cron-task-1
*/5 * * * *  you  cron-task-2
```

If you don’t want to use email for routine output, another method that works is sending the output to `syslog` with a tool like [`logger(1)`](http://linux.die.net/man/1/logger):

```
0 * * * *   you  cron-task | logger -it cron-task
```

Alternatively, you can configure aliases on your system to forward system mail destined for you on to an address you check. For Postfix, you’d use an [`aliases(5)`](http://www.postfix.org/aliases.5.html) file.

I sometimes use this setup in cases where the task is expected to emit a few lines of output which might be useful for later review, but send `stderr` output via `MAILTO` as normal. If you’d rather not use `syslog`, perhaps because the output is high in volume and/or frequency, you can always set up a log file `/var/log/cron-task.log` … but don’t forget to add a [`logrotate(8)`](http://linux.die.net/man/8/logrotate) rule for it!

Put the tasks in their own shell script file
--------------------------------------------

Ideally, the commands in your `crontab(5)` definitions should only be a few words, in one or two commands. If the command is running off the screen, it’s likely too long to be in the `crontab(5)` file, and you should instead put it into its own script. This is a particularly good idea if you want to reliably use features of `bash` or some other shell besides POSIX/Bourne `/bin/sh` for your commands, or even a scripting language like Awk or Perl; by default, `cron(8)` uses the system’s `/bin/sh` implementation for parsing the commands.

Because `crontab(5)` files don’t allow multi-line commands, and have other gotchas like the need to escape percent signs `%` with backslashes, keeping as much configuration out of the actual `crontab(5)` file as you can is generally a good idea.

If you’re running `cron(8)` tasks as a non-system user, and can’t add scripts into a system bindir like `/usr/local/bin`, a tidy method is to start your own, and include a reference to it as part of your `PATH`. I favour `~/.local/bin`, and have seen references to `~/bin` as well. Save the script in `~/.local/bin/cron-task`, make it executable with `chmod +x`, and include the directory in the `PATH` environment definition at the top of the file:

```
PATH=/home/you/.local/bin:/usr/local/bin:/usr/bin:/bin
MAILTO=you@example.com

0 * * * *  you  cron-task
```

Having your own directory with custom scripts for your own purposes has a host of other benefits, but that’s another article…

Avoid /etc/crontab
------------------

If your implementation of `cron(8)` supports it, rather than having an `/etc/crontab` file a mile long, you can put tasks into separate files in `/etc/cron.d`:

```
$ ls /etc/cron.d
system-a
system-b
raid-maint
```

This approach allows you to group the configuration files meaningfully, so that you and other administrators can find the appropriate tasks more easily; it also allows you to make some files editable by some users and not others, and reduces the chance of edit conflicts. Using `sudoedit(8)` helps here too. Another advantage is that it works better with version control; if I start collecting more than a few of these task files or to update them more often than every few months, I start a Git repository to track them:

```
$ cd /etc/cron.d
$ sudo git init
$ sudo git add --all
$ sudo git commit -m "First commit"
```

If you’re editing a `crontab(5)` file for tasks related only to the individual user, use the `crontab(1)` tool; you can edit your own `crontab(5)` by typing `crontab -e`, which will open your `$EDITOR` to edit a temporary file that will be installed on exit. This will save the files into a dedicated directory, which on my system is `/var/spool/cron/crontabs`.

On the systems maintained by the author, it’s quite normal for `/etc/crontab` never to change from its packaged template.

Include a timeout
-----------------

`cron(8)` will normally allow a task to run indefinitely, so if this is not desirable, you should consider either using options of the program you’re calling to implement a timeout, or including one in the script. If there’s no option for the command itself, the [`timeout(1)`](http://linux.die.net/man/1/timeout) command wrapper in `coreutils` is one possible way of implementing this:

```
0 * * * *  you  timeout 10s cron-task
```

Greg’s wiki has some further suggestions on [ways to implement timeouts](http://mywiki.wooledge.org/BashFAQ/068).

Include file locking to prevent overruns
----------------------------------------

`cron(8)` will start a new process regardless of whether its previous runs have completed, so if you wish to avoid locking for long-running task, on GNU/Linux you could use the [`flock(1)`](http://linux.die.net/man/1/flock) wrapper for the [`flock(2)`](http://linux.die.net/man/2/flock) system call to set an exclusive lockfile, in order to prevent the task from running more than one instance in parallel.

```
0 * * * *  you  flock -nx /var/lock/cron-task cron-task
```

Greg’s wiki has some more in-depth discussion of the [file locking](http://mywiki.wooledge.org/BashFAQ/045) problem for scripts in a general sense, including important information about the caveats of “rolling your own” when `flock(1)` is not available.

If it’s important that your tasks run in a certain order, consider whether it’s necessary to have them in separate tasks at all; it may be easier to guarantee they’re run sequentially by collecting them in a single shell script.

Do something useful with exit statuses
--------------------------------------

If your `cron(8)` task or commands within its script exit non-zero, it can be useful to run commands that handle the failure appropriately, including cleanup of appropriate resources, and sending information to monitoring tools about the current status of the job. If you’re using Nagios Core or one of its derivatives, you could consider using `send_nsca` to send passive checks reporting the status of jobs to your monitoring server. I’ve written [a simple script called `nscaw`](https://sanctum.geek.nz/cgit/nscaw.git/about) to do this for me:

```
0 * * * *  you  nscaw CRON_TASK -- cron-task
```

Consider alternatives to `cron(8)`
----------------------------------

If your machine isn’t always on and your task doesn’t need to run at a specific time, but rather needs to run once daily or weekly, you can install [`anacron`](http://linux.die.net/man/8/anacron) and drop scripts into the `cron.hourly`, `cron.daily`, `cron.monthly`, and `cron.weekly` directories in `/etc`, as appropriate. Note that on Debian and Ubuntu GNU/Linux systems, the default `/etc/crontab` contains hooks that run these, but they run only if [`anacron(8)`](http://linux.die.net/man/8/anacron) is not installed.

If you’re using `cron(8)` to poll a directory for changes and run a script if there are such changes, on GNU/Linux you could consider using a daemon based on `inotifywait(1)` instead.

Finally, if you require more advanced control over when and how your task runs than `cron(8)` can provide, you could perhaps consider writing a daemon to run on the server consistently and fork processes for its task. This would allow running a task more often than once a minute, as an example. Don’t get too bogged down into thinking that `cron(8)` is your only option for any kind of asynchronous task management!

参考：

* [Cron best practices](https://blog.sanctum.geek.nz/cron-best-practices/)
* [Better logging for cronjobs? Send cron output to syslog?](https://serverfault.com/a/434902)
* [My best practice with cron is to not use cron if possible. Systemd has timers with practically the same functionality and you'll never worry about:](https://news.ycombinator.com/item?id=30636872)