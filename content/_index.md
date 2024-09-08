---
title: Blog Of Mobileophone724
cascade:
  math: true
  toc: true
  type: docs
---

## 0x0 Whoami
- freshman in database
- coredump analyzer (one must analyze his own coredump)

## 0x1 TOP FIVE NEWEST
- [index related in PostgreSQL](index-in-pg)
- [从零开始证明RSA](zero2rsa)
- [paper reaading of roaring bitmap](0x01)
- [MESI: paper reading](0x04)
- [Constant Time Recovery in Azure SQL Database: paper reading](0x05)

## 0x11 DOING
- 0x08: [create index](0x08) #doing
- 0x09: [create index concurrently](0x09) #doing
- 0x0A: [create index parallelly](0x0a) #doing

## 0x2 PostgreSQL
### 0x21 Basic
- [build postgresql from source](0x00)

### 0x22 SLRU RELATED
- The reason and implement of [simple lru](slru)
- [commit log: the visibility of transactions](clog)
- #todo [subtransaction]
- #todo [multitransaction](multi-transaction)

### 0x23 WAL RELATED
- [log based database](database-log)
- [The idea of WAL](wal-basic)
- [Generate a WAL log](wal-insert)
- #todo [IO method of WAL]
- #todo [Decode a WAL]
- #todo [WAL level]

### 0x24 DDL
- [principle of pg_repack and online ddl](pg_repack)
- #todo [nbtree index]
- #todo [index access method]
- #doing  [column schema change](column-schema-change)

### 0x25 data representation
- #doing  [page representation](heap-page-representation)
- #todo  [nbtree representation](nbtree-representation)

### 0x2F others of PostgreSQL
- [ssl in pg](ssl-in-pg)
- [pgvector](pgvector)
- [hash join](hashjoin)
- [sequence type](sequence_type)

## 0x3 Others
- [google f1 file system](google-f1)
- [从零开始证明RSA](zero2rsa)
- [linux file interface](linux-file)
- [cublas related](cublasdgemmtutor)


## Archive
For each blog named with number, the map to name is give here

### 0x00 -- 0x10
- 0x00: [build postgresql from source](0x00)
- 0x01: [roaring bitmap: paper reaading](0x01)
- 0x02: [TAO: paper reading](0x02) #todo
- 0x03: [Multitransaction](0x03) #todo
- 0x04: [MESI: paper reading](0x04)
- 0x05: [Constant Time Recovery in Azure SQL Database: paper reading](0x05)
- 0x06: [Number of Reversed Inode](0x06)
- 0x07: ["-fwrapv" option in gcc](0x07)
- 0x08: [create index](0x08)
- 0x09: [create index concurrently](0x09)
- 0x0A: [create index parallelly](0x0a)
- 0x0B: [Everyday PostgreSQL](0x0b)