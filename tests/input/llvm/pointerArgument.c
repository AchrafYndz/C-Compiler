#include <stdio.h>

// Should print the numbers: 42 42 43 43 44 44 45 45

void f(int* a){
//	(*a)++; /*! not supported !*/
}

int main(){
	int x = 0;
	int* xp = &x;
	*xp = 42;
	printf("%d; ", x);
	printf("%d\n", *xp);
//	(*xp)++; /*! not supported */
	printf("%d; ", x);
	printf("%d\n", *xp);
	f(&x);
	printf("%d; ", x);
	printf("%d\n", *xp);
	f(xp);
	printf("%d; ", x);
	printf("%d\n", *xp);

	return 1;
}
