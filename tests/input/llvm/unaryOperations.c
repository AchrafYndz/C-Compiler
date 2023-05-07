#include <stdio.h>

// This should print the numbers 9 - 14
int main(){
	int x = 9;
    int a[2];
	printf("%d; ", -(-9));
    printf("%d; ", ++x);
    a[0] = 15;
	a[1] = 12;
	x = 12;
//	printf("%d; ", --a[1]); /*! not supported !*/
    printf("%d; ", x++);
    printf("%d; ", x);
//	a[0]--; /*! not supported !*/
    printf("%d; ", a[0]);
    return 1;
}
