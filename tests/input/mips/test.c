#include <stdio.h>

int main() {
    char b = 'b';
    b = 'd';
    int c =  (b + (b * 3)) / b;
    printf("%i", c);
    return 0;
}