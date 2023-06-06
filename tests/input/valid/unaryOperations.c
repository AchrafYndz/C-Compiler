#include <stdio.h>

// This should print the numbers 9 - 14
int main(){
	int x = 9;
    int a[2];
	printf("%d; ", -(-9));
    ++x;
    printf("%d; ", x);
    a[0] = 15;
	a[1] = 12;
	x = 12;
	int t1 = a[1];
	--t1;
	printf("%d; ", t1);
    printf("%d; ", x);
    x++;
    printf("%d; ", x);
    int t2 = a[0];
    t2--;
    printf("%d; ", t2);
    return 1;
}
