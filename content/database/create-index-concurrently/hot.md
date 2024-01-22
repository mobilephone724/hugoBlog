---
title: HOT
author: mobilephone724
math: true
weight: 2
prev:
---

# Simply Speaking

Simply speaking, a technical to reduce the table and index **bloat** caused by **updating**, through a link from old tuple(dead tuple) to new tuple **if the changed attribute isn't in any indexes**. With such links:

1. No need to generate a **new index entry** to represent the new tuple.
2. Old versions of updated tuples can be actually **removed by normal operations** instead of vacuum operation only

## related posts

[postgreSQL HOT From ZhiHu](https://zhuanlan.zhihu.com/p/455983543)

[OFFICIAL DOC](https://www.postgresql.org/docs/current/storage-hot.html)

For more details , see `postgresql/src/backend/access/heap/README.HOT`

Main Commits:

* `282d2a03dd30804b01f8042f640d638c2ee76604`  HOT updates
* `6f10eb21118f1ce72d4dd144c494749e25658d51`  Refactor heap_page_prune

# HIGH LEVEL DESIGN

## TID

![image-20240121153315316](https://raw.githubusercontent.com/mobilephone724/blog_pictures/master/heap-tuple-header.2024_01_21_1705848176.png)

HEAP PAGE

![image-20240122220305837](https://raw.githubusercontent.com/mobilephone724/blog_pictures/master/heap_page.2024_01_22_1705934933.png)

# Low Level Design

## Key functions

### heap_page_prune

###  `heap_page_prune_opt` 

> Optionally prune and repair fragmentation in the specified page.

```c
heap_page_prune_opt()
{
  minfree = RelationGetTargetPageFreeSpace();
  minfree = Max(minfree, BLCKSZ / 10);
  
  if (PageIsFull(page) || PageGetHeapFreeSpace(page) < minfree)
  {
    if (!ConditionalLockBufferForCleanup(buffer))
      continue;
    if (PageIsFull(page) || PageGetHeapFreeSpace(page) < minfree)
    {
      heap_page_prune();
    }
  }
}
```

### `heap_page_prune`

>  Prune and repair fragmentation in the specified page.

```c
heap_page_prune()
{
	for (offnum = FirstOffsetNumber;
		 	 offnum <= maxoff;
       offnum = OffsetNumberNext(offnum))
  {
  	heap_prune_chain(&prstate)
  }
  
  if (prstate.nredirected > 0 || prstate.ndead > 0 || prstate.nunused > 0)
  {
    heap_page_prune_execute();
  }
		 
}

```

### `heap_prune_chain`

> Prune specified line pointer or a HOT chain originating at line pointer.

```c
heap_prune_chain()
{
	/* while not end of the chain */
	for (;;)
	{
		lp = PageGetItemId(dp, offnum);
		/* Unused item obviously isn't part of the chain */
		if (!ItemIdIsUsed(lp))
			break;
			
		if (ItemIdIsRedirected(lp))
    {
			if (nchain > 0)
				break;			/* not at start of chain */
			chainitems[nchain++] = offnum;
			offnum = ItemIdGetRedirect(rootlp);
			continue;
    }
    
    if (ItemIdIsDead(lp))
      break;
    
    htup = (HeapTupleHeader) PageGetItem(dp, lp);
    
    /*
		 * Check the tuple XMIN against prior XMAX, if any
		 */
		if (TransactionIdIsValid(priorXmax) &&
			!TransactionIdEquals(HeapTupleHeaderGetXmin(htup), priorXmax))
			break;

 		/* record each item of this chain */
   	chainitems[nchain++] = offnum;
    
    switch ((HTSV_Result) prstate->htsv[offnum])
    {
    	case: HEAPTUPLE_DEAD:
      	tupdead = true;
        break;
      case HEAPTUPLE_RECENTLY_DEAD:
        heap_prune_record_prunable(prstate,
										   						 HeapTupleHeaderGetUpdateXid(htup));
      ...
    }
    
	}
  
  if (OffsetNumberIsValid(latestdead))
  {
    for (i = 1; (i < nchain) && (chainitems[i - 1] != latestdead); i++)
		{
			heap_prune_record_unused(prstate, chainitems[i]);
			ndeleted++;
		}
    
    if (i >= nchain) /* The whole chain is dead */
    	heap_prune_record_dead(prstate, rootoffnum);
    else						/* Or just redirect */
			heap_prune_record_redirect(prstate, rootoffnum, chainitems[i]);
  }
}
```

> `heap_prune_record_redirect` 

### `heap_page_prune_execute`

> Perform the actual page changes needed by heap_page_prune

```C
void
heap_page_prune_execute()
{
  /* redirect */
  for (int i = 0; i < nredirected; i++)
  {
    ItemIdSetRedirect(fromlp, tooff);
	}
  
  /* dead */
  for (int i = 0; i < ndead; i++)
  {
		ItemIdSetDead(lp);
  }
  
  /* unused */
  for (int i = 0; i < nunused; i++)
  {
    ItemIdSetUnused(lp);
	}
  PageRepairFragmentation();
  page_verify_redirects();
}
```



### search HOT chain

>  `heap_hot_search_buffer` search HOT chain for tuple satisfying snapshot

```C
bool
heap_hot_search_buffer()
{
  blkno = ItemPointerGetBlockNumber(tid);
  offnum = ItemPointerGetOffsetNumber(tid);
  for (;;)
  {
    lp = PageGetItemId(page, offnum);
    heapTuple->t_data = (HeapTupleHeader) PageGetItem(page, lp);

    
  }
}
```

