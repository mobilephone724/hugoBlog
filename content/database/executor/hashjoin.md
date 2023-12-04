---
title: hash join
author: mobilephone724
math: true
weight: 2
---

## background
From (How to use Hash Joins in PostgreSQL?)[https://minervadb.xyz/how-to-use-hash-joins-in-postgresql/],
Hash joins are often used in the following scenarios:
1. Large data sets: Hash joins are well-suited for large data sets where one of
   the tables is smaller than the other.
2. Equality joins
3. High selectivity: a small number of rows are returned as a result of the join.
4. Query performance optimization:
5. Data warehousing:

Execute the below SQL to use hash join
```SQL
drop table test;
drop table test2;
create table test(a text, b text);
insert into test select 'aaaaaa', 'bbbbbb' from generate_series(1, 500000);
create table test2(a text, b text);
insert into test2 select 'aaaaaa', 'bbbbbb' from generate_series(1, 50);
explain select * from test x join test2 y on x.a = y.a;
```

## high level view
simple hash join
![Alt text](/database/executor/hashjoin/One-pass_hash_join.svg)

![Alt text](/database/executor/hashjoin/parallel_two-pass_hash_join.svg)

## basic

This chapter shows the single thread hash join.

### inner join
[What is inner join](https://www.w3schools.com/sql/sql_join_inner.asp)

This is the simplest join method in hash join. So we introduce a simple hash
join state machine here. (See `ExecHashJoinImpl` for detail )

What's `batch`
Since we can't allocate as much memory as we want, instead of building a hash
table of the entire table, PG split the tables to several `batches` where all
tuples have the same hash value flag.

See [Queries in PostgreSQL: 6. Hashing](https://postgrespro.com/blog/pgsql/5969673)

```
START WITH:
    state ==> HJ_BUILD_HASHTABLE

case HJ_BUILD_HASHTABLE:
    state ==> HJ_NEED_NEW_OUTER

case HJ_NEED_NEW_OUTER:
    ### generate a new outer tuple
    state ==> HJ_NEED_NEW_BATCH ### No more tuple in this batch.
          ==> HJ_SCAN_BUCKET;   ### Find a outer tuple. Can this one matches a
                                    inner one?

case HJ_SCAN_BUCKET:
    ### Scan the selected hash bucket for matches to current outer
    state ==> HJ_NEED_NEW_OUTER ### Whether we can find a match or not, we
                                    always generate a new outer tuple.

case HJ_NEED_NEW_BATCH:
    ### Try to advance to next batch
    state ==> HJ_NEED_NEW_OUTER;
          ==> FINISH
```

### right join
To complete right join, we can just emit each outer tuple even if there's no
matched innner tuple.
```
case HJ_SCAN_BUCKET:
    state ==> HJ_FILL_OUTER_TUPLE  ### Can not find a match. Is it a left join?
          ==> HJ_NEED_NEW_OUTER

case HJ_FILL_OUTER_TUPLE:
    state ==> HJ_NEED_NEW_OUTER;    ### Whether emit the outer tuple with
                                        null-filled left tuple or not, we always
                                        generate a new outer tuple.
```

### left join
To complete this, we must remember whether a inner tuple has been matched. So
```
case HJ_NEED_NEW_OUTER:
    state ==> HJ_FILL_INNER_TUPLES  ### This batch has been finished, see if
                                        there are unmatched inner tuples.
          ==> HJ_NEED_NEW_BATCH
          ==> HJ_SCAN_BUCKET

case HJ_FILL_INNER_TUPLES:
    state ==> HJ_NEED_NEW_BATCH     ### No more unmatched inner tuples, so start
                                        the next batch
          ==> HJ_FILL_INNER_TUPLES  ### return an unmatched inner tuple.
```

### summary
Until now, we can generate a full state machine in non-parallel mode
```
START WITH:
    state ==> HJ_BUILD_HASHTABLE

case HJ_BUILD_HASHTABLE:
    state ==> HJ_NEED_NEW_OUTER

case HJ_NEED_NEW_OUTER:
    ### generate a new outer tuple
    state ==> HJ_FILL_INNER_TUPLES  ### This batch has been finished, see if
                                        there are unmatched inner tuples.
          ==> HJ_NEED_NEW_BATCH ### No more tuple in this batch.
          ==> HJ_SCAN_BUCKET;   ### Find a outer tuple. Can this one matches a
                                    inner one?

case HJ_SCAN_BUCKET:
    ### Scan the selected hash bucket for matches to current outer
    state ==> HJ_FILL_OUTER_TUPLE  ### Can not find a match. Is it a left join?
          ==> HJ_NEED_NEW_OUTER ### Whether we can find a match or not, we
                                    always generate a new outer tuple.

case HJ_NEED_NEW_BATCH:
    ### Try to advance to next batch
    state ==> HJ_NEED_NEW_OUTER;
          ==> FINISH
```

## parallel hash
`BarrierArriveAndWait` will increase current phase

Let introduce the state machine first
```
START WITH:
case HJ_BUILD_HASHTABLE:
    ### If multi-batch, we need to hash the outer relation up front.
    ExecParallelHashJoinPartitionOuter(node);
    state ==> HJ_NEED_NEW_BATCH ### Select a batch to work on.

case HJ_NEED_NEW_OUTER:
    ExecParallelHashJoinOuterGetTuple
        sts_parallel_scan_next
    
case HJ_NEED_NEW_BATCH:
    ExecParallelHashJoinNewBatch()
        switch PHJ_BATCH_STATE
            case PHJ_BATCH_ELECT:
                ### One backend allocates the hash table
                ExecParallelHashTableAlloc
                ### Fall through
            case PHJ_BATCH_ALLOCATE:
                ### Wait for allocation to complete and Fall through
            case PHJ_BATCH_LOAD:
                ### Start (or join in) loading tuples and Fall through.
            case PHJ_BATCH_PROBE:
                ### This batch is ready to probe
                ExecParallelHashTableSetCurrentBatch
                return true;
            case PHJ_BATCH_SCAN:
                ### detach and go around again
            case PHJ_BATCH_FREE:
    state ==> HJ_NEED_NEW_OUTER

```

```
    PHJ_BUILD_ELECT ==> PHJ_BUILD_ALLOCATE
```

```
ExecParallelHashJoinNewBatch
```