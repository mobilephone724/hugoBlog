---
title: lsmTree
slug: lsmtree-2fapmq
url: /post/lsmtree-2fapmq.html
date: '2025-03-03 22:34:36+08:00'
lastmod: '2025-03-03 23:36:34+08:00'
toc: true
isCJKLanguage: true
---



# lsmTree

### **LSM-Tree 简介**

LSM-Tree（Log-Structured Merge-Tree）是一种为高写入吞吐设计的存储结构，广泛应用于 NoSQL 数据库（如 LevelDB、RocksDB）。其核心思想是将随机写入转换为顺序写入，并通过分层合并优化数据管理。

‍

​![lsmtree](assets/lsmtree-20250303233520-zn8ytar.png)​

---

#### **LSM-Tree 的核心组件**

1. **MemTable**

    * 内存中的可变数据结构（通常为跳表或平衡树），用于快速处理写入操作。
    * 写入数据时，首先插入 MemTable。
    * 当 MemTable 达到阈值时，转为不可变的 SSTable 并写入磁盘。
2. **SSTable（Sorted String Table）**

    * 磁盘上的不可变有序文件，按层级组织。
    * 每层包含多个 SSTable，高层级的数据量是低层级的倍数（如 10 倍）。
3. **Compaction（合并）**

    * 当某层 SSTable 数量超过阈值时，触发合并操作。
    * 合并相邻层的 SSTable，去重并删除无效数据，生成新的 SSTable 到下一层。

---

#### **LSM-Tree 操作流程**

1. **写入**：数据先写入 MemTable。
2. **读取**：先查 MemTable，再逐层查询 SSTable。
3. **删除**：插入一个删除标记（Tombstone），合并时清理数据。
4. **合并**：后台线程将小 SSTable 合并为大 SSTable，减少查询时的 I/O 开销。

---

### **C++ 实现简易 LSM-Tree**

#### **1. 内存表（MemTable）实现**

使用 `std::map`​ 模拟内存中的有序结构。

```cpp
#include map>
#include string>
#include vector>
#include fstream>
#include sstream>

class MemTable {
private:
    std::map<std::string, std::string> data;
    size_t max_size;
    bool tombstone = false;

public:
    MemTable(size_t max_size = 1024) : max_size(max_size) {}

    // 插入或更新键值对
    void put(const std::string& key, const std::string& value) {
        data[key] = value;
        if (data.size() >= max_size) {
            tombstone = true; // 标记为可转储
        }
    }

    // 标记删除
    void remove(const std::string& key) {
        data[key] = "TOMBSTONE";
    }

    // 查找键值
    std::string get(const std::string& key) {
        auto it = data.find(key);
        if (it != data.end()) {
            return it->second;
        }
        return "";
    }

    // 判断是否需要转储到磁盘
    bool need_flush() const {
        return tombstone;
    }

    // 获取所有键值对（按序）
    std::vector<std::pair<std::string, std::string>> export_data() {
        return std::vector<std::pair<std::string, std::string>>(data.begin(), data.end());
    }

    // 清空内存表
    void clear() {
        data.clear();
        tombstone = false;
    }
};
```

---

#### **2. SSTable 实现**

将内存表数据写入有序文件，支持从文件加载数据。

```cpp
class SSTable {
private:
    std::string filename;

public:
    SSTable(const std::string& filename) : filename(filename) {}

    // 将内存表数据写入 SSTable 文件
    void write(const std::vector<std::pair<std::string, std::string>>& data) {
        std::ofstream file(filename, std::ios::binary);
        for (const auto& entry : data) {
            file < entry.first < "," < entry.second < "\n";
        }
        file.close();
    }

    // 从 SSTable 文件中查找键值
    std::string read(const std::string& key) {
        std::ifstream file(filename, std::ios::binary);
        std::string line;
        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string k, v;
            std::getline(iss, k, ',');
            std::getline(iss, v);
            if (k == key) {
                return v;
            }
        }
        return "";
    }
};
```

---

#### **3. LSM-Tree 主逻辑**

管理内存表和 SSTable 的层级合并。

```cpp
#include vector>
#include filesystem>
namespace fs = std::filesystem;

class LSMTree {
private:
    MemTable memtable;
    std::vector<std::vector<SSTable>> levels;
    size_t level0_max = 4;  // Level 0 最多容纳 4 个 SSTable

public:
    LSMTree() {
        levels.resize(2);  // 简化实现：仅 Level 0 和 Level 1
    }

    // 插入数据
    void put(const std::string& key, const std::string& value) {
        memtable.put(key, value);
        if (memtable.need_flush()) {
            flush_memtable();
        }
    }

    // 删除数据
    void remove(const std::string& key) {
        memtable.remove(key);
        if (memtable.need_flush()) {
            flush_memtable();
        }
    }

    // 查找数据
    std::string get(const std::string& key) {
        // 先查内存表
        std::string value = memtable.get(key);
        if (!value.empty()) {
            return (value == "TOMBSTONE") ? "[DELETED]" : value;
        }

        // 再查磁盘中的 SSTable（从 Level 0 到 Level 1）
        for (auto& level : levels) {
            for (auto& sstable : level) {
                value = sstable.read(key);
                if (!value.empty()) {
                    return (value == "TOMBSTONE") ? "[DELETED]" : value;
                }
            }
        }
        return "[NOT FOUND]";
    }

private:
    // 将内存表转储为 Level 0 的 SSTable
    void flush_memtable() {
        auto data = memtable.export_data();
        std::string filename = "sstable_level0_" + std::to_string(levels[0].size()) + ".dat";
        SSTable sstable(filename);
        sstable.write(data);
        levels[0].push_back(sstable);
        memtable.clear();

        // 触发 Level 0 合并
        if (levels[0].size() >= level0_max) {
            compact_level(0);
        }
    }

    // 合并层级
    void compact_level(int level) {
        std::vector<SSTable> merged_tables;
        std::vector<std::pair<std::string, std::string>> merged_data;

        // 读取当前层级所有 SSTable 的数据
        for (auto& sstable : levels[level]) {
            // 模拟读取所有键值对（实际需实现迭代器）
            std::ifstream file(sstable.filename);
            std::string line;
            while (std::getline(file, line)) {
                std::istringstream iss(line);
                std::string key, value;
                std::getline(iss, key, ',');
                std::getline(iss, value);
                merged_data.emplace_back(key, value);
            }
            file.close();
            fs::remove(sstable.filename); // 删除旧文件
        }

        // 去重和删除标记处理
        std::map<std::string, std::string> temp_map;
        for (const auto& entry : merged_data) {
            if (entry.second != "TOMBSTONE") {
                temp_map[entry.first] = entry.second;
            } else {
                temp_map.erase(entry.first);
            }
        }

        // 写入下一层级
        std::vector<std::pair<std::string, std::string>> new_data(temp_map.begin(), temp_map.end());
        std::string filename = "sstable_level1_" + std::to_string(levels[1].size()) + ".dat";
        SSTable new_sstable(filename);
        new_sstable.write(new_data);
        levels[1].push_back(new_sstable);

        // 清空当前层级
        levels[level].clear();
    }
};
```

---

#### **4. 测试示例**

```cpp
#include iostream>

int main() {
    LSMTree lsm;

    // 插入数据
    lsm.put("name", "Alice");
    lsm.put("age", "30");
    std::cout < "Get name: " < lsm.get("name") < std::endl;  // Alice

    // 删除数据
    lsm.remove("age");
    std::cout < "Get age: " < lsm.get("age") < std::endl;    // [DELETED]

    // 强制触发合并
    for (int i = 0; i  5; i++) {
        lsm.put("key" + std::to_string(i), "value" + std::to_string(i));
    }
    std::cout < "Get key3: " < lsm.get("key3") < std::endl;  // value3

    return 0;
}
```

---

### **实现说明**

1. **MemTable**：使用 `std::map`​ 模拟有序内存表，支持插入、删除和查找。
2. **SSTable**：将数据按 CSV 格式写入文件，简化查询逻辑。
3. **合并策略**：当 Level 0 的 SSTable 数量超过阈值时，合并到 Level 1。
4. **删除处理**：通过 Tombstone 标记实现惰性删除，合并时清理数据。

---

### **优化方向**

1. **跳表实现**：替换 `std::map`​ 为自定义跳表，提高并发写入性能。
2. **Bloom Filter**：为 SSTable 添加布隆过滤器，加速查询。
3. **多线程合并**：后台线程异步执行合并操作，避免阻塞写入。
4. **文件格式优化**：使用二进制格式（如 Protobuf）存储 SSTable，减少 I/O 开销。

---

通过上述实现，可以理解 LSM-Tree 的核心设计思想，并在此基础上扩展为生产级存储引擎。

‍
