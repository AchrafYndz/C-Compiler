#include <stdio.h>

int main() {
    int a = 3;
    int * b = &a;
    int ** c = &b;
    int * d = *c;
    int e = *d;

    printf("%i", e);
    return 0;
}