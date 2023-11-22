---
title: pg16 summary
author: mobilephone724
math: true
weight: 2
prev: /database/pg_xact/slru/slru
---

## What's this?
Summary some new features and its commitid. These complement will be shared later
(if possible)

## Content

### From Release Note
* feature: parallel hash join
  * commit id: 11c2d6fdf5af1aacec
  * lines: 7 files changed, 323 insertions(+), 48 deletions(-)
  * discussion: [PostgreSQL: Parallel Full Hash Join](https://www.postgresql.org/message-id/CA%2BhUKG%2BA6ftXPz4oe92%2Bx8Er%2BxpGZqto70-Q_ERwRaSyA%3DafNg@mail.gmail.com)
  * difficulty level: extremely hard
* feature: Improve performance of vacuum freezing
  * 
  


### From pganalyz
> https://pganalyze.com/blog/5mins-postgres-16-faster-copy-bulk-load
* feature: fast copy
  * commit id: many commits
      * 26158b852d3adf69360  "Use ExtendBufferedRelTo() in XLogReadBufferExtended()"
      * 00d1e02be2498718011  "hio: Use ExtendBufferedRelBy() to extend tables more efficiently"
      * 5279e9db8e8da3c310c  "heapam: Pass number of required pages to RelationGetBufferForTuple()"
      * acab1b0914e426d2878  "Convert many uses of ReadBuffer[Extended](P_NEW) to ExtendBufferedRel()"
      * fcdda1e4b50249c344e5  "Use ExtendBufferedRelTo() in {vm,fsm}_extend()"
      * 31966b151e6ab7a6284  "bufmgr: Introduce infrastructure for faster relation extension"
      * 12f3867f5534754c8bac  "bufmgr: Support multiple in-progress IOs by using resowner"
      * dad50f677c42de20716  "bufmgr: Acquire and clean victim buffer separately"
      * 794f25944790ed0462c  "bufmgr: Add Pin/UnpinLocalBuffer()"
      * 4d330a61bb1969df31f "Add smgrzeroextend(), FileZero(), FileFallocate()"
  * discussion:  [PostgreSQL: refactoring relation extension and BufferAlloc(), faster COPY](https://www.postgresql.org/message-id/20221029025420.eplyow6k7tgu6he3@awork3.anarazel.de)
  * difficulty level: very hard
* feature: fast relation extension
  * commit id: see above
