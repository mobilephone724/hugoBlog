---
title: 跳表的实现
slug: implementation-of-skipping-tables-299fl1
url: /post/implementation-of-skipping-tables-299fl1.html
date: '2025-03-03 22:46:11+08:00'
lastmod: '2025-03-04 23:35:01+08:00'
toc: true
isCJKLanguage: true
---



# 跳表的实现

之前还没有写过跳表，补一下实现，

​![skip_table](https://raw.githubusercontent.com/mobilephone724/hugoBlog/siyuan-pub/images/skip_table-20250304233140-hzl983v.png)​

FROM deepseek

### 跳表（Skip List）原理详解

跳表是一种基于有序链表的高效数据结构，通过引入多层索引实现快速查找，其平均时间复杂度为O(log n)，与平衡树相当，但实现更简单。以下是其核心原理：

#### **1. 跳表结构**

* **多层链表**：每个节点包含多个前向指针（层），层数由概率决定（通常为1/2的概率升级到更高层）。
* **头节点（Header）** ：作为起始点，不存储实际数据，最高层指向链表的首个元素。
* **尾节点（Tail）** ：所有层的指针指向NULL，表示链表结束。

#### **2. 关键操作原理**

* **插入**：

  1. 随机生成新节点的层数（如抛硬币直到出现反面）。
  2. 从最高层开始查找插入位置，记录每层的前驱节点。
  3. 在各层的前驱和后继之间插入新节点，更新指针。
* **查找**：

  1. 从最高层开始，向右遍历直到当前节点的下一节点值大于目标值。
  2. 下移一层继续查找，重复直到最底层。
  3. 若找到相等节点则返回，否则不存在。
* **删除**：

  1. 类似查找过程，定位目标节点及其各层前驱。
  2. 更新各层前驱的指针，绕过目标节点。
  3. 释放目标节点内存。

#### **3. 时间复杂度**

* **平均情况**：O(log n)（基于概率平衡的层数分布）。
* **最坏情况**：O(n)（所有节点仅1层，退化为普通链表）。

‍

## 自己的实现

```c++
#include <bits/stdc++.h>

using namespace std;

class skip_table
{

    struct jump_node
    {
        int key, value;
        vector<jump_node *> next;
        const int _level;
        jump_node(int k, int v, int size, int level) : _level(level)
        {
            key = k;
            value = v;
            next = vector<jump_node *>(size, nullptr);
        }
        int level()
        {
            return _level;
        }
    };

public:
    skip_table(int level) : _level(level)
    {
        _head = new jump_node(0, 0, level, level);
    }

    bool insert(int k, int v, bool replace = true)
    {
        vector<jump_node *> prev_node(_level, nullptr);
        auto p = _head;

        for (int l = _level - 1; l >= 0; --l)
        {
            while (p->next[l] && p->next[l]->key < k)
            {
                p = p->next[l];
            }
            prev_node[l] = p;
        }

        if (p->next[0] && p->next[0]->key == k)
        { // if found
            if (!replace)
            {
                return false;
            }

            p->next[0]->value = v;
            return true;
        }

        // not found, insert new one
        int new_node_level = random_level();
        auto new_node = new jump_node(k, v, _level, new_node_level);
        for (int i = 0; i < new_node_level; ++i)
        {
            new_node->next[i] = prev_node[i]->next[i];
            prev_node[i]->next[i] = new_node;
        }

        return true;
    }

    bool remove(int k)
    {
        vector<jump_node *> prev_node(_level, nullptr);
        auto p = _head;

        for (int l = _level - 1; l >= 0; --l)
        {
            while (p->next[l] && p->next[l]->key < k)
            {
                p = p->next[l];
            }
            prev_node[l] = p;
        }

        if (p->next[0] && p->next[0]->key == k)
        {
            auto pending_delete = p->next[0];
            for (int i = 0; i < _level; ++i)
            {
                prev_node[i]->next[i] = pending_delete->next[i];
            }
            delete pending_delete;
            return true;
        }

        return false;
    }

    int get(int k, bool &found)
    {
        auto p = _head;
        for (int l = _level - 1; l >= 0; --l)
        {
            while (p->next[l] && p->next[l]->key < k)
            {
                p = p->next[l];
            }
        }

        if (p->next[0] && p->next[0]->key == k)
        {
            found = true;
            return p->next[0]->value;
        }
        else
        {
            found = false;
            return -1;
        }
    }

    void print()
    {
        for (int i = _level - 1; i >= 0; --i)
        {
            auto p = _head->next[i];
            cout << "LEVEL: " << i << "\t";
            while (p != nullptr)
            {
                cout << p->key << " : " << p->value << " ---> ";
                p = p->next[i];
            }
            cout << endl;
        }
    }

private:
    jump_node *_head;
    const int _level;

    int random_level()
    {
        int level = 1;
        for (int i = 1; i < _level; ++i)
        {
            if (random_bool())
            {
                level++;
            }
        }

        return level;
    }

    bool random_bool()
    {
        static std::random_device rd;  // Seed for the random number generator
        static std::mt19937 gen(rd()); // Mersenne Twister engine

        // Define a distribution for generating 0 or 1
        static std::uniform_int_distribution<int> dist(0, 1);

        // Generate a random value (0 or 1)
        return dist(gen) == 1;
    }
};

int gen_random_val()
{
    static std::random_device rd;  // Seed for the random number generator
    static std::mt19937 gen(rd()); // Mersenne Twister engine

    static int lower_bound = 1;
    static int upper_bound = 10000;
    static std::uniform_int_distribution<> dist(lower_bound, upper_bound);

    // Generate a random number
    return dist(gen);
}

int main()
{
    auto *st = new skip_table(100);
    auto mp = map<int, int>();

    auto compare_jp_with_mp = [&st, &mp](int key)
    {
        bool error = false;
        bool found_jp = false;
        int val_jp = st->get(key, found_jp);

        auto iter_mp = mp.find(key);
        bool found_mp = iter_mp != mp.end();

        if (found_jp != found_mp)
        {
            if (found_mp)
            {
                cout << "map found but st not found " << endl;
            }
            else
            {
                cout << "st found but map not found " << endl;
            }

            cout << key << ":" << endl;
            error = true;
        }
        else if (found_jp)
        {
            if (val_jp != iter_mp->second)
            {
                cout << "both found but st = " << val_jp << " while mp = " << iter_mp->second;
                error = true;
            }
        }

        if (error)
        {
            st->print();
            exit(1);
        }

        return true;
    };

    // {
    //     auto start = std::chrono::high_resolution_clock::now();
    //     for (int i = 0; i <= 1000000; ++i)
    //     {
    //         int key = gen_random_val();
    //         int val = gen_random_val();

    //         st->insert(key, val);
    //         // st->print();
    //     }
    //     auto end = std::chrono::high_resolution_clock::now();
    //     auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    //     std::cout << "JP INSERT Time taken: " << duration.count() << " microseconds" << std::endl;
    // }

    // {
    //     auto start = std::chrono::high_resolution_clock::now();
    //     for (int i = 0; i <= 1000000; ++i)
    //     {
    //         int key = gen_random_val();
    //         int val = gen_random_val();

    //         mp[key] = val;
    //         // st->print();
    //     }
    //     auto end = std::chrono::high_resolution_clock::now();
    //     auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    //     std::cout << "MP INSERT Time taken: " << duration.count() << " microseconds" << std::endl;
    // }

    for (int i = 0; i <= 10000; ++i)
    {
        int key = gen_random_val();
        int val = gen_random_val();

        mp[key] = val;
        st->insert(key, val);
        cout << "insert " << key << ":" << val << endl;
        // st->print();
    }

    for (int i = 0; i <= 5000; ++i)
    {
        int key = gen_random_val();

        mp.erase(key);
        st->remove(key);
    }

    for (int i = 0; i <= 10000; ++i)
    {
        int key = gen_random_val();

        compare_jp_with_mp(key);
    }

    return 0;
}
```

‍

‍

## deepseek的实现

未验证该代码。（deepseek 日常漏掉 "<")

```c++
#include iostream>
#include vector>
#include cstdlib>
#include ctime>
#include climits>

template typename K, typename V>
class SkipList {
private:
    struct Node {
        K key;
        V value;
        std::vector<Node*> forward; // 各层的前向指针

        Node(K k, V v, int level) : key(k), value(v), forward(level, nullptr) {}
    };

    Node* header;    // 头节点（哨兵）
    int max_level;   // 最大层数限制
    int current_level; // 当前最大层数
    float probability; // 层数增长概率
    int size;          // 节点数量

    // 生成随机层数
    int random_level() {
        int level = 1;
        while ((static_cast<float>(rand()) / RAND_MAX)  probability && level  max_level) {
            level++;
        }
        return level;
    }

public:
    // 构造函数
    SkipList(int max_level = 16, float prob = 0.5) 
        : max_level(max_level), probability(prob), current_level(1), size(0) {
        header = new Node(K(), V(), max_level);
        srand(time(0));
    }

    // 析构函数
    ~SkipList() {
        Node* current = header->forward[0];
        while (current != nullptr) {
            Node* next = current->forward[0];
            delete current;
            current = next;
        }
        delete header;
    }

    // 插入键值对
    void insert(const K& key, const V& value) {
        std::vector<Node*> update(max_level, nullptr);
        Node* current = header;

        // 查找各层的前驱节点
        for (int i = current_level - 1; i >= 0; i--) {
            while (current->forward[i] != nullptr && current->forward[i]->key  key) {
                current = current->forward[i];
            }
            update[i] = current;
        }

        // 检查是否已存在相同键
        current = current->forward[0];
        if (current != nullptr && current->key == key) {
            current->value = value; // 更新值
            return;
        }

        // 生成新节点的层数
        int new_level = random_level();
        if (new_level > current_level) {
            for (int i = current_level; i  new_level; i++) {
                update[i] = header;
            }
            current_level = new_level;
        }

        // 创建新节点并更新指针
        Node* new_node = new Node(key, value, new_level);
        for (int i = 0; i  new_level; i++) {
            new_node->forward[i] = update[i]->forward[i];
            update[i]->forward[i] = new_node;
        }
        size++;
    }

    // 查找键对应的值
    bool search(const K& key, V& value) {
        Node* current = header;
        for (int i = current_level - 1; i >= 0; i--) {
            while (current->forward[i] != nullptr && current->forward[i]->key  key) {
                current = current->forward[i];
            }
        }
        current = current->forward[0];
        if (current != nullptr && current->key == key) {
            value = current->value;
            return true;
        }
        return false;
    }

    // 删除键
    bool remove(const K& key) {
        std::vector<Node*> update(max_level, nullptr);
        Node* current = header;

        // 查找各层的前驱节点
        for (int i = current_level - 1; i >= 0; i--) {
            while (current->forward[i] != nullptr && current->forward[i]->key  key) {
                current = current->forward[i];
            }
            update[i] = current;
        }

        current = current->forward[0];
        if (current == nullptr || current->key != key) {
            return false; // 未找到
        }

        // 更新各层指针
        for (int i = 0; i  current_level; i++) {
            if (update[i]->forward[i] != current) break;
            update[i]->forward[i] = current->forward[i];
        }

        delete current;
        size--;

        // 降低当前层数（若高层为空）
        while (current_level > 1 && header->forward[current_level - 1] == nullptr) {
            current_level--;
        }
        return true;
    }

    // 打印跳表结构（调试用）
    void display() {
        std::cout < "Skip List (Level=" < current_level < ", Size=" < size < "):" < std::endl;
        for (int i = current_level - 1; i >= 0; i--) {
            Node* node = header->forward[i];
            std::cout < "Level " < i < ": ";
            while (node != nullptr) {
                std::cout < node->key < "(" < node->value < ") ";
                node = node->forward[i];
            }
            std::cout < std::endl;
        }
    }
};

// 示例测试
int main() {
    SkipList<int, std::string> skiplist;

    // 插入数据
    skiplist.insert(3, "Alice");
    skiplist.insert(6, "Bob");
    skiplist.insert(7, "Charlie");
    skiplist.insert(9, "Dave");
    skiplist.insert(12, "Eve");

    // 查找测试
    std::string value;
    if (skiplist.search(6, value)) {
        std::cout < "Key 6 found: " < value < std::endl; // 输出 Bob
    }

    // 删除测试
    if (skiplist.remove(7)) {
        std::cout < "Key 7 removed." < std::endl;
    }

    // 显示跳表结构
    skiplist.display();

    return 0;
}

```
