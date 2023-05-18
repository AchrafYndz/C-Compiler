.data
hello_world_0: .asciiz "hello world"
%s_1: .asciiz "%s"
goodbye_world_2: .asciiz "goodbye world"

.text
x:
.4byte 3
main:
jr $ra
nop
