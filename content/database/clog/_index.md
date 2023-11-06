---
title: CLOG
author: mobilephone724
math: true
draft: true

---

## 概述
本文主要包含以下模块的代码阅读

1. `clog.c`：上层的`clog`功能接口
2. `slru.c`：clog的基石，“简单的” in memroy lru模块



## clog 部分

仅考虑xact相关的实现，主要的功能为和事务状态交互

1. `TransactionIdSetTreeStatus` ：设置事务状态
2. `TransactionIdGetStatus`：获取事务状态

以及一些其他与vacuum相关功能：

1. `ExtendCLOG`：新增一个`clog`文件
2. `TruncateCLOG`：删除不需要的`clog`文件

### TransactionIdGetStatus

从clog文件中获取事务状态

```c
XidStatus
TransactionIdGetStatus(TransactionId xid, XLogRecPtr *lsn)
{
	int			pageno = TransactionIdToPage(xid);
	int			byteno = TransactionIdToByte(xid);
	int			bshift = TransactionIdToBIndex(xid) * CLOG_BITS_PER_XACT;

    slotno = SimpleLruReadPage_ReadOnly()
    byteptr = XactCtl->shared->page_buffer[slotno] + byteno;
    status = (*byteptr >> bshift) & CLOG_XACT_BITMASK;
}
```

与heap的`shared_buffer` 不同，这里的路径是独立的`page_buffer`。



## slru部分

### 存储结构

#### clog的存储结构

1. 一个CLOG文件有32个page（pg的page，即8k），

```
#define SLRU_PAGES_PER_SEGMENT	32
```

2. 一个事务的状态有4种，需要2个bits

```c
#define TRANSACTION_STATUS_IN_PROGRESS		0x00
#define TRANSACTION_STATUS_COMMITTED		0x01
#define TRANSACTION_STATUS_ABORTED			0x02
#define TRANSACTION_STATUS_SUB_COMMITTED	0x03
```

3. 则一个clog文件可以存储$32 * 8 * 1024 * 8/2 = 1048576$个事务的状态（有无page header？似乎没有）
    
```C
#define CLOG_BITS_PER_XACT	2
#define CLOG_XACTS_PER_BYTE 4
#define CLOG_XACTS_PER_PAGE (BLCKSZ * CLOG_XACTS_PER_BYTE)
#define CLOG_XACT_BITMASK	((1 << CLOG_BITS_PER_XACT) - 1)
```

4. xid在`0xffffffff`处wraparound，故clog文件在`4096`处wraparound
5. 我通过一下方式可通过xid计算其在clog文件中的位置

```C
/* which page contains the xid */
#define TransactionIdToPage(xid)	((xid) / (TransactionId) CLOG_XACTS_PER_PAGE)
/* xid offset in the page */
#define TransactionIdToPgIndex(xid) ((xid) % (TransactionId) CLOG_XACTS_PER_PAGE)

/* which byte in the page contains the xid */
#define TransactionIdToByte(xid)	(TransactionIdToPgIndex(xid) / CLOG_XACTS_PER_BYTE)
/* xid offset in the byte */
#define TransactionIdToBIndex(xid)	((xid) % (TransactionId) CLOG_XACTS_PER_BYTE)
```

#### 内存slru

全局共享的buffer管理数组。

```C
typedef struct SlruSharedData
{
	LWLock	   *ControlLock;

	/* Number of buffers managed by this SLRU structure */
	int			num_slots;

	/*
	 * Arrays holding info for each buffer slot.  Page number is undefined
	 * when status is EMPTY, as is page_lru_count.
	 */
	char	  **page_buffer;
	SlruPageStatus *page_status;
	bool	   *page_dirty;
	int		   *page_number;
	int		   *page_lru_count;
	LWLockPadded *buffer_locks;

	/*----------
	 * We mark a page "most recently used" by setting
	 *		page_lru_count[slotno] = ++cur_lru_count;
	 * The oldest page is therefore the one with the highest value of
	 *		cur_lru_count - page_lru_count[slotno]
	 * The counts will eventually wrap around, but this calculation still
	 * works as long as no page's age exceeds INT_MAX counts.
	 *----------
	 */
	int			cur_lru_count;

	/*
	 * latest_page_number is the page number of the current end of the log;
	 * this is not critical data, since we use it only to avoid swapping out
	 * the latest page.
	 */
	int			latest_page_number;
} SlruSharedData;
```

从内存结构上看，是一个数组，每个元素代表一个page。同时，记录这些page的使用次数。

```
page_lru_count[slotno] = ++cur_lru_count;
```



各个进程独有的pointer

```C
/*
 * Which set of functions to use to handle a given request.  The values of
 * the enumerators must match the indexes of the function table in sync.c.
 */
typedef enum SyncRequestHandler
{
	SYNC_HANDLER_MD = 0,
	SYNC_HANDLER_CLOG,
	SYNC_HANDLER_COMMIT_TS,
	SYNC_HANDLER_MULTIXACT_OFFSET,
	SYNC_HANDLER_MULTIXACT_MEMBER,
	SYNC_HANDLER_NONE
} SyncRequestHandler;

/*
 * SlruCtlData is an unshared structure that points to the active information
 * in shared memory.
 */
typedef struct SlruCtlData
{
	SlruShared	shared;

	/*
	 * Which sync handler function to use when handing sync requests over to
	 * the checkpointer.  SYNC_HANDLER_NONE to disable fsync (eg pg_notify).
	 */
	SyncRequestHandler sync_handler;

	/*
	 * Decide whether a page is "older" for truncation and as a hint for
	 * evicting pages in LRU order.  Return true if every entry of the first
	 * argument is older than every entry of the second argument.  Note that
	 * !PagePrecedes(a,b) && !PagePrecedes(b,a) need not imply a==b; it also
	 * arises when some entries are older and some are not.  For SLRUs using
	 * SimpleLruTruncate(), this must use modular arithmetic.  (For others,
	 * the behavior of this callback has no functional implications.)  Use
	 * SlruPagePrecedesUnitTests() in SLRUs meeting its criteria.
	 */
	bool		(*PagePrecedes) (int, int);

	/*
	 * Dir is set during SimpleLruInit and does not change thereafter. Since
	 * it's always the same, it doesn't need to be in shared memory.
	 */
	char		Dir[64];
} SlruCtlData;
```

slru并不仅用于clog，还包括了`commit_ts`，`multixact`等模块。



### 核心功能

1. `SimpleLruZeroPage`：新增一个page
2. `SimpleLruReadPage` ：读一个page
3. `SimpleLruWritePage` ：写一个page