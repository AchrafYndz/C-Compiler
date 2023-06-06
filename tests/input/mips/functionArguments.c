#include <stdio.h>

int mult(int x, int y) {
    return x * y;
}

int square(int x) {
    return x * 3;
}

int main(){
    int c = 2;
    c++;
    int b = c * 3;
    printf("%i", b);
    int a = square(b * 3);
    printf("%i", a);
    int d = mult(a, b);
    printf("%i", d);
}
