---
title: DDIA--Encoding and Evolution(1)
slug: ddiaencoding-and-evolution-1-2dgaes
url: /post/ddiaencoding-and-evolution-1-2dgaes.html
date: '2025-03-18 23:03:23+08:00'
lastmod: '2025-03-18 23:30:22+08:00'
toc: true
isCJKLanguage: true
---



# DDIA--Encoding and Evolution(1)

## Compatibility

* Backward compatibility: Newer code can read data that was written by older code.
* Forward compatibility: Older code can read data that was written by newer code.

‍

## Thrift and Protocol Buffers

Apache Thrift and Protocol Buffers (protobuf) are binary encoding libraries that are based on the same principle.

‍

In Thrift, you would describe the schema in the Thrift **interface definition language** (**IDL**) like this:

```c++
struct Person {
1: required string userName,
2: optional i64 favoriteNumber,
3: optional list<string> interests
}
```

‍

The equivalent schema definition for Protocol Buffers looks very similar:

```c++
message Person {
required string user_name = 1;
optional int64 favorite_number = 2;
repeated string interests = 3;
}
```

‍

### Thrift BinaryProtocol

​![image](https://raw.githubusercontent.com/mobilephone724/hugoBlog/siyuan-pub/images/image-20250318230834-58zd7vk.png)​

Each field has  **(1)a type annotation** (to indicate whether it is a string, integer, list, etc.) and, where required, (2)**a length indication** (length of a string, number of items in a list).

There are no field names (userName, favoriteNumber, interests). Instead, the encoded data contains **field tags**, which are numbers (1, 2, and 3).

‍

### Thrift CompactProtocol

​![image](https://raw.githubusercontent.com/mobilephone724/hugoBlog/siyuan-pub/images/image-20250318231100-ske1qmo.png)​

It packs the same information into only 34 bytes. It does this by (1) **packing the field type and tag number into a single byte**, and by (2)**using variable-length integers**. Rather than using a full eight bytes for the number 1337, it is encoded in two bytes, **with the top bit of each byte used to indicate whether there are still more bytes to come.**

See "**Base 128 Varint Encoding**" for detail

‍

## Protocol Buffers

​![image](https://raw.githubusercontent.com/mobilephone724/hugoBlog/siyuan-pub/images/image-20250318232012-d80u44j.png)​

‍

in the schemas shown earlier, each field was marked either required or optional, but this makes no difference to how the field is encoded (nothing in the binary data indicates whether a field was required). The difference is simply that required enables a runtime check that fails if the field is not set, which can be useful for catching bugs.

‍

## Field tags and schema evolution

We said previously that schemas inevitably need to change over time. We call this **schema evolution**.

> Each field is identified by its tag number (the numbers 1, 2, 3 in the  
> sample schemas) and annotated with a datatype (e.g., string or integer).  **(1)**  If a field value is not set, it is simply omitted from the encoded record. From this you can see that field tags are critical to the meaning of the encoded data.  **(2)** You can change the name of a field in the schema, since the encoded data never refers to field names, but you cannot change a field’s tag, since that would make all existing encoded data invalid.

1. Omit a non-set value
2. change the name instead of the tag

‍

>  You can add new fields to the schema, provided that you give each field a new tag number. If old code (which doesn’t know about the new tag numbers you added) tries to read data written by new code, including a new field with a tag number it doesn’t recognize, it can simply ignore that field. The datatype annotation allows the  
> parser to determine how many bytes it needs to skip. This maintains forward compatibility: old code can read records that were written by new code.

Old code ignores the tag that it doesn't recognize

‍

>  What about backward compatibility? As long as each field has a unique tag number, new code can always read old data, because the tag numbers still have the same meaning. The only detail is that if you add a new field, you cannot make it required. If you were to add a field and make it required, that check would fail if new code read data written by old code, because the old code will not have written the new field that you added. Therefore, to maintain backward compatibility, every field you add after the initial deployment of the schema must be optional or have a default value.

New added field can't be required

‍

> Removing a field is just like adding a field, with backward and forward compatibility concerns reversed. That means you can only remove a field that is optional (a required field can never be removed), and you can never use the same tag number again (because you may still have data written somewhere that includes the old tag number, and that field must be ignored by new code).

Can remove optional field only and can't use the same tag number again.

‍

## **Base 128 Varint Encoding**

**Base 128 Varint Encoding** is a method used to encode integers into a variable number of bytes, where each byte represents a 7-bit chunk of the integer. The most significant bit (MSB) of each byte is used as a flag to indicate whether there are more bytes to follow. This approach allows smaller integers to be stored in fewer bytes, optimizing space efficiency.

---

### **How it Works**

1. **Split the Integer into 7-bit Chunks**  
    The integer is divided into groups of 7 bits, starting from the least significant bit (LSB). Each group is stored in a separate byte.
2. **Add the MSB Flag**

    * If there are more 7-bit chunks to encode, the MSB of the byte is set to `1`​.
    * If the current byte is the last one, the MSB is set to `0`​.
3. **Store the Bytes**  
    The bytes are stored in sequence, with the least significant byte first.

---

### **Encoding Process**

1. Convert the integer to its binary representation.
2. Split the binary number into 7-bit chunks, starting from the LSB.
3. For each chunk, add the MSB flag:

    * Set MSB to `1`​ if there are more chunks.
    * Set MSB to `0`​ if it's the last chunk.
4. Store the resulting bytes in order.

---

### **Example: Encoding the Integer** **​`300`​**​

1. **Binary Representation of 300**:  
    ​`100101100`​ (9 bits)
2. **Split into 7-bit Chunks**:

    * ​`0101100`​ (LSB, first chunk)
    * ​`0000010`​ (MSB, second chunk)
3. **Add MSB Flags**:

    * First chunk: `10101100`​ (`0xAC`​) (MSB set to `1`​ because there’s another chunk).
    * Second chunk: `00000010`​ (`0x02`​) (MSB set to `0`​ because it’s the last chunk).
4. **Final Encoded Result**:  
    ​`[0xAC, 0x02]`​

---

### **Key Points**

* **MSB as a Continuation Flag**:  
  The MSB of each byte indicates whether the next byte is part of the same integer.
* **Variable-Length Encoding**:  
  Smaller integers use fewer bytes, while larger integers use more bytes.
* **Efficiency**:  
  This method is particularly efficient for encoding small integers, as it avoids the fixed overhead of using a fixed number of bytes (e.g., 4 bytes for a 32-bit integer).

---

### **Decoding Process**

To decode a Varint-encoded integer:

1. Read each byte sequentially.
2. Check the MSB of each byte:

    * If MSB is `1`​, the next byte is part of the same integer.
    * If MSB is `0`​, the current byte is the last one.
3. Combine the 7-bit chunks to reconstruct the original integer.

---

### **Why Use Base 128 Varint Encoding?**

* **Space Savings**:  
  It reduces the number of bytes needed to store integers, especially for small values.
* **Flexibility**:  
  It can handle integers of arbitrary size without requiring a fixed-length format.
* **Compatibility**:  
  It is widely used in protocols like Thrift and Protocol Buffers for efficient data serialization.

---

### **Summary**

Base 128 Varint Encoding is a compact and efficient way to store integers by splitting them into 7-bit chunks and using the MSB of each byte as a continuation flag. This method is particularly useful in scenarios where space optimization is critical, such as in network protocols or data storage systems.
