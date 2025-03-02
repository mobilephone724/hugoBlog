---
title: 可串行化的实现思路
slug: implementation-ideas-for-serialization-z2idq9y
url: /post/implementation-ideas-for-serialization-z2idq9y.html
date: '2025-03-02 22:13:38+08:00'
lastmod: '2025-03-02 23:13:32+08:00'
toc: true
isCJKLanguage: true
---



# 可串行化的实现思路

paper: https://drkp.net/papers/ssi-vldb12.pdf

## 可串行化冲突的例子

* **wr-dependencies**: if T1 writes a version of an object, and T2 reads that version, then T1 appears to have executed before T2
* **ww-dependencies**: if T1 writes a version of some object, and T2 replaces that version with the next version, then T1 appears to have executed before T2
* **rw-antidependencies**: *if T1 writes a version of some object, and T2 reads the previous version of that object, then T1 appears to have executed after T2, because T2 did not see its update*. As we will see, these dependencies are central to SSI; we sometimes also refer to them as rw-conflicts.

​![image](https://raw.githubusercontent.com/mobilephone724/hugoBlog/siyuan-pub/images/image-20250302223239-pdjy6rq.png)​

‍

Note that the definitions above referred to objects. We use this more abstract term rather than “tuple” or “row” because dependencies can also be caused by predicate reads. For example, if T1 scans a table for all rows where x \= 1, and T2 subsequently inserts a new row matching that predicate, then there is a T1 --rw--> T2 rw-antidependency.

### 定理一

**Theorem 1** (Fekete et al. [10]). Every cycle in the serialization history graph contains a sequence of edges T1 --rw−→ T2 --rw−→ T3 where each edge is a rw-antidependency. Furthermore, T3 must be the first transaction in the cycle to commit.

‍

## PostgreSQL 的实现思路：

### 只检测相邻的 rw 依赖

However, rather than testing the graph for cycles, it checks for a “dangerous structure” of two adjacent rw-antidependency edges. If any transaction has both an incoming rw-antidependency and an outgoing one, SSI aborts one of the transactions involved.

只检测相邻的 rw 依赖会造成假阳

### 减少假阳导致性能下降

PSSI (Precisely Serializable Snapshot Isolation) is an extension of SSI that does eliminate all false positives , PSSI can reduce the abort rate by up to 40% . We considered this approach for PostgreSQL, but rejected it because we felt the costs outweighed the benefits of the reduced false positive abort rate.

### 优化只读事务

#### 只读快照的顺序优化

First, the theory enables a ***read-only snapshot ordering optimization*** to reduce the false-positive abort rate.

例子：

That every cycle contains a dangerous structure T1 --rw-> T2 --rw-> T3, where T3 is the first to commit. Thus, even if a dangerous structure is found, no aborts are necessary if either T1 or T2 commits before T3. 参考 “定理一”

#### 定理三

Theorem 3. Every serialization anomaly contains a dangerous structure T1 --rw−→ T2 --rw−→ T3, where if T1 is read-only, T3 must have committed before T1 took its snapshot.

#### 安全快照

在 T 获取快照前，如果不存在两个已提交的事务，它们间有 rw-antidependency，则 T 的快照是安全快照。

Safe snapshots: A read-only transaction T has a safe snapshot if no concurrent read/write transaction has committed with a rw-antidependency out to a transaction that committed before T’s snapshot, or has the possibility to do so.

#### Deferrable Transactions

为了避免长的只读事务造成 SSI 冲突（**SIREAD 锁冲突**：只读事务需要为所有访问的数据记录 SIREAD 锁（用于跟踪读写依赖））：

Deferrable transactions, a new feature, **provide a way to ensure that complex read-only transactions will always run on a safe snapshot.**

```pgsql
BEGIN TRANSACTION READ ONLY, DEFERRABLE.
```

‍
