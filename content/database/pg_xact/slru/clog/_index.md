---
title: CLOG
author: mobilephone724
math: true

---

## 概述
本文主要包含以下模块的代码阅读

1. `clog.c`：上层的`clog`功能接口
2. `slru.c`：clog的基石，“简单的” in memroy lru模块



## slru





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