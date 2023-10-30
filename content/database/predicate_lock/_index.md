---

weight: 3

title: "Phantoms Predicate Lock"


author: "mobilephone724"

tags: ["Lock"]

categories: ["database"]

toc:

 enable: true

 auto: true

date: 2022-11-21T22:01:56+08:00

publishDate: 2022-01-17T22:41:38+08:00

---
# Intro
## Phantoms
The idea comes from which is an object, the table or its each tuple. The former
is unacceptable. But the latter, when tupples appear or disappear from a table,
select statements can conflict with the change, which is called the phantoms.

## Predicate Lock
Although predicate lock is too expensive, it's a good way to think about things.

predicate lock can be writen like
```
<tid, [slock|xlock], predicate>
```

Two predicate locks are compatible iff
```
tid1 = tid2 (a transaction can't conflict with itself), or
both are slock (no changes makes no conflict ), or
predicate1 and predicate2 can't be satisfied at the same time
```

When applying the lock system, use two structure, a granted set and a waiting list.
1. Each time a tx requries a predicate lock, the system compares the lock with each
other in the granted set and waiting list. If the predicate lock is compatibal, add it
to granted set, otherwise to waiting list.
2. Each time a tx ends, remove all its predicated lock from both the granted set and
the waiting list. And grant each predicate lock in the waiting list if it's compatible now,
until reach the end of the list or encouter an incompatible predicate lock.

# The problem with predicate locks

1. 