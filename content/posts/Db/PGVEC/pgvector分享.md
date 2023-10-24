# 序言
`pgvector`是一个向量搜索（根据近似度）的插件，用来加速AKNN（approximate nearest neighbor）。
`PASE`提到，向量ANN算法包括4类
1. tree-based algorithms
    1. KD-Tree
    2. RTree
2. quantization-based algorithms
    1. IVFFlat
    2. IVFADC
    3. IMI
3. graph based algorithms
    1. HNSW
    2. NSG
    3. SSG
4. hash-base algorithms
    1. LSH
`pgvector` 包括两个算法，`IVFFlat` 和 `HNSW`，后续内容将以这两个算法的内容及其实现展开。


# IVFFlat
IVFFlat 算法主要包括以下几个步骤
+ 预处理阶段
    + 使用 `KMeans` 将数据集划分成多个簇(cluster)
+ 查询阶段
    + 通过每个簇的中心点（向量是高维的点）获取N个最近的簇
    + 遍历这N个簇的所有点，从中找到最近的K个点
## KMeans算法
reference [k-means clustering - Wikipedia](https://en.wikipedia.org/wiki/K-means_clustering)
简要描述：选取K个中心点，使得数据集中的所有点到其最近的中心点“距离”之和最近，以平方和距离为例：

Given a set of observations $(x_1, x_2, \dot, x_n)$, where each observation is a $d$\-dimensional real vector, k-means clustering aims to partition the $n$ observations into $k$ ($\leq n$) sets $S = {S_1, S_2, \dot, S_k}$ so as to minimize the within-cluster sum of squares (WCSS). Formally, the objective is to find:
```
\math
```
