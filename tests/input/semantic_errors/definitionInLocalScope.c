#include <ShouldBeValid.h> // Why is this invalid?

int main(){
    // definition of f in local scope
    void f(int a, int b){
        a*b;
    }
}
