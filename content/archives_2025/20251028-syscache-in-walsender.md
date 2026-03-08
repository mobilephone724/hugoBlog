---
title: "syscache in walsender"
date: 2025-10-28T23:31:52+08:00
# draft: true
---


## Question And Answer

Q: How does the walsender to update the syscache after a ddl?

A: Briefly, in PG17, the walsender invalidate the cache when handle the
REORDER_BUFFER_CHANGE_INVALIDATION message and rebuild the cache through
historical MVCC snapshot. They are both implemented in the reorder buffer.


## syscache and its version

For a normal postgres backend, the syscache is always the latest version
through the database level. Although it doesn't match the MVCC requirements
exactly, it is **correct** since ddl always requires a heavy lock.

This feature brings a very fantastic feature, that one syscache has only one
version at a time through the whole database system. And note that the
generating of WAL records is like mapping the concurrent changes into time
series changes -- in LSN order.

So, for a walsender, decoding the WAL is like a time travel. A walsender only
needs to generate a syscache once for decoding all current running TXNs until
the next invalidating message.

## invalidation and rebuilding

invalidation: Code path in reorder buffer:

```txt
ReorderBufferProcessTXN
\__ ReorderBufferExecuteInvalidations
	\__ LocalExecuteInvalidationMessage
```


rebuilding: Code path affected by reorder buffer:

```txt
ReorderBufferProcessTXN
\__ SetupHistoricSnapshot
\__ case REORDER_BUFFER_CHANGE_INTERNAL_SNAPSHOT:
	\__ SetupHistoricSnapshot
\__ case REORDER_BUFFER_CHANGE_INTERNAL_COMMAND_ID:
	\__ SetupHistoricSnapshot

SearchCatCacheInternal
\__ SearchCatCacheMiss
	\__ table_open
	\__ systable_beginscan
		\__ GetCatalogSnapshot(relid)
			\__ if (HistoricSnapshotActive())
```

