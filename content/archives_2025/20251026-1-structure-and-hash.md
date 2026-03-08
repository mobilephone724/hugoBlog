---
title: "C Structure Align And Hash Key"
date: 2025-10-26T21:26:45+08:00
# draft: true
---

## Structure Alignment
In C language, structure size, besides the types it contains, is decided by
the two alignment rules.
1. Each member's offset must be a multiple of its alignment requirement.
2. The overall structure size must be a multiple of its largest member's
   alignment requirement.

For expample, consider the following structure:
```c
struct A {
    int32 a;
    int64 b;
};
```
The actural memory layout of this structure is:

```txt
0 -- 3  bytes --> | int32 a  |
4 -- 7  bytes --> | padding  |
8 -- 15 bytes --> | int64 b  |
```

If we reorder the members of the structure as follows:
```c
struct B {
    int64 b;
    int32 a;
};
```
The actural memory layout of this structure is:

```txt
0  -- 7  bytes --> | int64 b  |
8  -- 11 bytes --> | int32 a  |
12 -- 16 bytes --> | padding  |
```

In this case, we cannot reduce the size of the structure by reordering its
members.


## Hash Key
In postgresql, hash key can be self-designed structures. When designing this
struture as above:

```c
struct hash_key {
    int64 b;
    int32 a;
};
```

There is a problem that the padding bytes (12 -- 16 bytes) are not initialized.
And since in default, hash function will calculate the hash value based on the
whole structure bytes, which means the padding bytes are also included in the
hash calculation. And thus the hash value is not stable!

There are several ways to solve this problem:
1. Rearrange the structure members to eliminate padding bytes (which is impossible
   in this case).
2. Manually initialize the padding bytes to zero
3. Define an extra member to occupy the padding space.
4. Use a self-defined hash function that only considers the actual members of the
   structure, excluding the padding bytes.
5. Use compiler-specific attributes or pragmas to control structure packing.


In way 2, it is easy to forget to initialize the padding bytes.

In way 3, it is not elegant to add extra members just for padding, especially
I have to initialize these extra members whenever I initialize the structure.

In way 4, it is a bit complex to write a custom hash function, especially I have
to consider the distribution of hash values to avoid collisions. But it is the
most portable and general way.

In way 5, it may lead to performance issues due to misaligned accesses and it's
compiler-specific. But in not-performance-critical scenarios, this trade-off
might be acceptable for the sake of simplicity and correctness.

Consider the hash table (unordered_map) in C++, the most common way is to define
a custom hash function (way 4) and equality comparator for the key structure.

Below is how to use way 5 in GCC/Clang to pack the structure:
```c
#include <stdint.h>
#include <stdio.h>

struct __attribute__((__packed__)) hash_key {
    int64 b;
    int32 a;
};

int main()
{
    printf("Size of packed hash_key: %zu\n", sizeof(struct hash_key));
    return 0;
}

/*
 * Size of packed hash_key: 12
 */