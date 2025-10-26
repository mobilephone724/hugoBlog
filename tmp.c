#include <stdint.h>
#include <stdio.h>

struct __attribute__((__packed__)) hash_key {
    int64_t b;
    int32_t a;
};

int main()
{
    printf("Size of packed hash_key: %zu\n", sizeof(struct hash_key));
    return 0;
}