---
title: mesi-summary
slug: me-z1ogd4d
url: /post/me-z1ogd4d.html
date: '2025-03-29 08:56:22+08:00'
lastmod: '2025-03-29 09:35:38+08:00'
toc: true
isCJKLanguage: true
---



# mesi-summary

# 

## store buffer

### why?

when one cpu wants to change the data (not in modify or execlusive mode), it would always change it whatever messages others cpu returns.

**So just change the data in store buffer immediately.**

### complexity it introduces

* Multilayer caches(what is the reason of wmb): 

  * Example: Consider a cpu, it stores two value(A and B) sequencely where A in store buffer and B is in cache. We can decide whether another CPU could see the updated A before seeing B, since we have no idea that it receives the invalidate message before request the value of B.
  * Reason: Broadcast later changes(in cache) before previous changes (in store buffer) is actually seen by others.
* **Write** **memory barriar**: CPUs must wait until the store buffer is clear before performing later changes. (Or just store later changes in store buffer until all of the prior entries in the store buffer had been applied)

![image](https://raw.githubusercontent.com/mobilephone724/hugoBlog/siyuan-pub/images/image-20250329093456-j3puqdh.png)

‍

‍

## invalidate queue

### why?

When receive an  invalidate message, the cache line could be busy, that causes the long ackownledgement.

So just store the invalidate message in the invalidate queue, and deal the message later.

### complexity it introduces

**read** **memory barriar**: accepet all invalidate message before read subsequent values.

![image](https://raw.githubusercontent.com/mobilephone724/hugoBlog/siyuan-pub/images/image-20250329093503-406qo5f.png)
