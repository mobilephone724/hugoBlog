---
title: CLOG
author: mobilephone724
math: true
weight: 2
prev: /database/pg_xact/slru/slru


---

## Overview
This chapter explains the content of `clog`

`clog`(commit log), records the commit status of each transaction. The log
exists both in memory mannaged by `slru` buffer and disk for durability. The
commit status can be the four kinds below:
```C
#define TRANSACTION_STATUS_IN_PROGRESS		0x00
#define TRANSACTION_STATUS_COMMITTED		0x01
#define TRANSACTION_STATUS_ABORTED			0x02
#define TRANSACTION_STATUS_SUB_COMMITTED	0x03
```




## In-Disk Representation
Thinking that the commit status of each transaction composites an array `clog[]`
and `clog[xid]` records the status, we can easily store the array to disk by the
`slru`.

The status of one transaction needs two bits to represent:
```C
#define CLOG_BITS_PER_XACT	2
#define CLOG_XACTS_PER_BYTE 4
#define CLOG_XACTS_PER_PAGE (BLCKSZ * CLOG_XACTS_PER_BYTE)
#define CLOG_XACT_BITMASK	((1 << CLOG_BITS_PER_XACT) - 1)
```

So we can get the xid's index and offset in page and byte.
```C
#define TransactionIdToPage(xid)	((xid) / (TransactionId) CLOG_XACTS_PER_PAGE)
#define TransactionIdToPgIndex(xid) ((xid) % (TransactionId) CLOG_XACTS_PER_PAGE)
#define TransactionIdToByte(xid)	(TransactionIdToPgIndex(xid) / CLOG_XACTS_PER_BYTE)
#define TransactionIdToBIndex(xid)	((xid) % (TransactionId) CLOG_XACTS_PER_BYTE)
```

Thinking of that one slru segment contains 32 pages, so we name the clog file as
`0000`(contains xid in [0, 32 * CLOG_XACTS_PER_PAGE - 1]), `0001`(contains xid
in [32 * CLOG_XACTS_PER_PAGE, 32 * CLOG_XACTS_PER_PAGE * 2 - 1]) and so on.
Because four hex numbers can represent $16^4=2^12$ files with
$2^12 \times 2^5 \times 8192 \times 4 = 2^{32}$ transactions' status(a int32 size)

Attension, such simple mapping means that the pages in clog file don't have
page headers. So we can't record `LSN`, `checksum` in each page. The lack of
`LSN` means the changes of clog page wouldn't be recorded in `WAL` but clog
doesn't need it indeed.





