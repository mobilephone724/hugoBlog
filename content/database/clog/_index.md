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



## slru

### 简述

+ slru用来干什么？
    + slru是一个简单的buffer管理模块
+ 有了buffer pool manager，为什么还要slru？
    + bpm管理通用的page，比如heap，vm等
    + slru最大的特点就是lru，非常适合处理xid这样，递增的信息。
+ 有哪些模块使用slru？
    + `clog`, `commit_ts`,`multixid`,`subtrans`等等和事务相关的模块。所以它们都在`src/access/transam`目录下。

### 存储结构

与bpm不同，通过slru管理的page，其文件大小固定，一个文件有32个page，一个page有8KB，故一个文件最大为256K。

与WAL不同，WAL文件的大小在创建时就已经确定为16M，与WAL文件重用保持一致，而slru的文件，先在内存中产生相应的page，再会去落盘。

```c
#define SLRU_PAGES_PER_SEGMENT	32
```

####  内存slru

##### 全局 buffer 数组

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
} SlruSharedData;
```

从内存结构上看，是一个数组，每个元素代表一个page。同时，记录这些page的使用次数。

```
page_lru_count[slotno] = ++cur_lru_count;
```

同时每个page，都有状态标识，以确定脏页

```c
/*
 * Page status codes.  Note that these do not include the "dirty" bit.
 * page_dirty can be true only in the VALID or WRITE_IN_PROGRESS states;
 * in the latter case it implies that the page has been re-dirtied since
 * the write started.
 */
typedef enum
{
	SLRU_PAGE_EMPTY,			/* buffer is not in use */
	SLRU_PAGE_READ_IN_PROGRESS, /* page is being read in */
	SLRU_PAGE_VALID,			/* page is valid and not being written */
	SLRU_PAGE_WRITE_IN_PROGRESS /* page is being written out */
} SlruPageStatus;
```

##### 各个进程私有的pointer

```C

/*
 * SlruCtlData is an unshared structure that points to the active information
 * in shared memory.
 */
typedef struct SlruCtlData
{
	SlruShared	shared;

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

初始化时，即返回一个SlruCtlData

### 核心功能

1. `SimpleLruZeroPage`：新增一个page
2. `SimpleLruReadPage` ：读一个page
3. `SimpleLruWritePage` ：写一个page

#### 基础函数

选择一个空slot

```
/* Select the slot to re-use when we need a free slot. */
static int
SlruSelectLRUPage(SlruCtl ctl, int pageno)
{
	# loop -- It's a very clever design to dealing with corner cases
	#         such as the victim page being re-dirtied while we wrote it.
		# return if we have such a slot
		# return if we have an empty slot "SLRU_PAGE_EMPTY"
		# select a lru slot
			# return it if it's clean. Or
			# victim it if dirty
}
```

记录一个"most recently used"的page

```
#define SlruRecentlyUsed(shared, slotno)	\
	do { \
		int		new_lru_count = (shared)->cur_lru_count; \
		if (new_lru_count != (shared)->page_lru_count[slotno]) { \
			(shared)->cur_lru_count = ++new_lru_count; \
			(shared)->page_lru_count[slotno] = new_lru_count; \
		} \
	} while (0)
```



#### `SimpleLruZeroPage`：新增一个page

```
/* Initialize (or reinitialize) a page to zeroes. */
int
SimpleLruZeroPage(SlruCtl ctl, int pageno)
{
	slotno = SlruSelectLRUPage(ctl, pageno);
}
```



## clog 部分

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

#### 



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



3. 