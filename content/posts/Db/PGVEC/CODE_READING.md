---

weight: 3

title: "Basic Knowledge of Database Log"


author: "mobilephone724"

tags: ["log"]

categories: ["database"]

toc:

 enable: true

 auto: true

date: 2022-03-31T11:01:15+08:00

publishDate: 2022-03-31T11:01:15+08:00

---

# core algorithms and code

## HNSW
### INSERT


``` HnswInsertElement
/*
 * Algorithm 1 from paper: update graph by inserting an element
 * Parms:
 * @element: element to insert
 * @entryPoint: the initial entry point
 * @index?
 * @procinfo
 * @collation
 * @m: same as "M" in algo(number of established connections)
 */
HnswInsertElement(HnswElement element, HnswElement entryPoint,
    			  Relation index, FmgrInfo *procinfo, Oid collation,
    			  int m, int efConstruction, bool existing)
    level = element->level;
    q = PointerGetDatum(element->vec)

    # fill entry point list with the initial one
    ep = list_make1(HnswEntryCandidate(entryPoint,))

    # for layers upper than the element's level
    for (int lc = entryLevel; lc >= level + 1; lc--)
        # only get the nearest element now
        w = HnswSearchLayer()
        ep = w;

    # for the below layers
    for (int lc = level; lc >= 0; lc)
        # search for top efConstruction nearest ones
        w = HnswSearchLayer(efConstruction)

        lw = w

        # get neighbors
        neighbors = SelectNeighbors(lw, lm, lc, procinfo, collation, NULL);

        # add connection
        # Is this different from paper?
        #  bidirectional vs single directional
        #  shrink directions or not shrink
        AddConnections()
            foreach(lc2, neighbors)
        		a->items[a->length++] = *((HnswCandidate *) lfirst(lc2));

```

### search layer

```
/*
 * Algorithm 2 from paper: search this layer with specifiyed enter points to
 * return "ef" closest neighbors
 * Parms:
 *  @q: same as algo
 *  @ep: enter points
 *  @ef: count of closest neighbors
 *  @lc: layer number
 *  @index:
 *  @procinfo:
 *  @collation:
 *  @inserting:
 *  @skipElement:
 */
List *
HnswSearchLayer(Datum q, List *ep, int ef, int lc, Relation index,
                FmgrInfo *procinfo, Oid collation, int m, bool inserting,
                HnswElement skipElement)
    v = NULL.                 # visited points
    C = NULL                  # set of candidates, nearer first
    W = NULL                  # dynamic found nearest neighbors

    # for each candidate in enter points
    foreach(lc2, ep)
        hc = (HnswCandidate *) lfirst(lc2); # HNSW candidates
        v.add(hc)
        C.add(hc)
        W.add(hc)

    # loop until no more candidates
    while (!C.empty())
        c = C.pop_nearest()

        # for each neighbor "e" in the nearest candicate "c"
        neighborhood = &c->element->neighbors[lc];
        for (int i = 0; i < neighborhood->length; i++)
            # neighbor e
            HnswCandidate *e = &neighborhood->items[i];
            v.add(e)
            DO # continue if visited

            # f is the furthest element in dynamic neighbors
            f = W.furthest()

            # find a good neighbor who is closer to q than the worst one in W
            if (DISTANT(e, q) < DISTANT(f, q) || wlen < ef)
                ec = e
                # neighbor of ec can also be the candidates
                C.add(ec)
                # add ec to W to promote the lower bound
                W.add(ec)

                # clean W if it's too large
                if (skipElement == NULL ||
                    list_length(e->element->heaptids) != 0)
					wlen++;
					/* No need to decrement wlen */
					if (wlen > ef)
						W.pop_furthest
	return W
```

#### pairing heap
[配对堆 - OI Wiki (oi-wiki.org)](https://oi-wiki.org/ds/pairing-heap/)
* insert($\mathrm{log}n$)
* random_select($\mathrm{log} n$) select_min($\mathrm{log} n$) 
* delete_min($\mathrm{log} n$)
### select neighbors

```SelectNeighbors
/*
 * Algorithm 4: select neighbors starting with specified candidates
 * PARAMS:
 *  @c : candidates
 *  @m : number of neighbors to return
 *  @lc: layer number
 *  @
 *
 * NOTES:
 *  extendCandidates = false
 *  keepPrunedConnections = true
 *  pruned
 */
static List *
SelectNeighbors(List *c, int m, int lc, FmgrInfo *procinfo, Oid collation,
                HnswCandidate * *pruned)
    r = NULL    # results---returning neighbors 
    w = c       # working candidates
    wd = NULL;  # discarded candidates;

    # Since we don't extend candidates, if the starting candidates isn't enought
    # just return.
    if (list_length(w) <= m)
        return w

    # loop untils no more working candidate or enought neighbors
    while (length(w) > 0 && length(r) < m)
        *e = llast(w); # get the nearest candidates
        closer = CheckElementCloser(e, r, lc, procinfo, collation);
        if(closer)
            r.append(e)
        else
            wd.append(e)

    # loop until discarded candidates are empty or enough neighbors
    while (!wd.empty() && length(r) < m)
        r.append(wd.pop_nearest())
    
    prune = wd.nearest()
    return r
    
    
```


### data structure
```c
typedef struct HnswElementData
{
	List	   *heaptids;
	uint8		level;
	uint8		deleted;
	HnswNeighborArray *neighbors;
	BlockNumber blkno;
	OffsetNumber offno;
	OffsetNumber neighborOffno;
	BlockNumber neighborPage;
	Vector	   *vec;
}			HnswElementData;

typedef struct HnswCandidate
{
	HnswElement element;
	float		distance;
}			HnswCandidate;

typedef struct HnswNeighborArray
{
	int			length;
	HnswCandidate *items;
}			HnswNeighborArray;
```

NB: `HnswNeighborArray` is single direction, but what we need is bidirection. So, each when we call `AddConnections` to add a connection, we need to "repair" the neighbor array to 