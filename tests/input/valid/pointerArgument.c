#include <stdio.h>

// Should print the numbers: 42 42 43 43 44 44 45 45

void f(int* a){
	int b = *a;
	b++;
}

int main(){
	int x = 0;
	int* xp = &x;
	x = 42;
	printf("%d; ", x);
	printf("%d\n", *xp);
    x++;
	printf("%d; ", x);
	printf("%d\n", *xp);
	x++;
	printf("%d; ", x);
	printf("%d\n", *xp);
	x++;
	printf("%d; ", x);
	printf("%d\n", *xp);

	return 1;
}
