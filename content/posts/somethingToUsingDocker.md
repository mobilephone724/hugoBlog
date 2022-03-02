---
weight: 3
title: "something to using docker"
draft: false
author: "mobilephone724"
# description: "Hugo provides multiple built-in shortcodes for author convenience and to keep your markdown content clean."
tags: ["envirnment"]
categories: ["docker"]

lightgallery: true
toc:
  enable: true
  auto: true
date: 2022-01-14T23:43:08+08:00
publishDate: 2022-01-14T23:43:08+08:00
---

## set proxy

It's annoying that you can't download third-party libraries from github because of network when using linux os docker image to develop. So using proxy in docker is necessary.

[This is the official website to use proxy in docker](https://docs.docker.com/config/daemon/systemd/)

Below is one of the ways if you have root' permission

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo touch /etc/systemd/system/docker.service.d/proxy.conf
```
add the below content to `proxy.conf`
```bash
sudo touch /etc/systemd/system/docker.service.d/proxy.conf
```
then restart docker
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```
**notice:** This is not to say and docker container will connect to the port in your physics machine. You still need to install your vpn client in each of your containers.

## install libraries

It's common to find that a linux os container lacks of libraries when linking because linux docker image is minimal. So how to install libraries when getting a error like `cannot find -lcrc32c`? In ubuntu, you can install `libcrc*`.`l` means `lib` and you can use `tab` to autocompletion the library, and then you can find the library you need is `libcrcutil-dev`.