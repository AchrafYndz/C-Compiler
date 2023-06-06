#include <stdio.h>

// This should print: 10, 10, 11, 11
int main(){
	int x = 0;
	int* xp = &x;
	x = 10;
	printf("%d; ", x);
	printf("%d\n", *xp);
	x++;
	printf("%d; ", x);
	printf("%d\n", *xp);
	return 1;
}
