.data
hello_world_0: .asciiz "hello world"
%s_1: .asciiz "%s"
goodbye_world_2: .asciiz "goodbye world"

.text
move $fp, $sp
li $s0, 3
sw $s0, 0($gp)
li $s0, 97
sw $s0, -4($gp)
li $s0, 0x40400000
mtc1 $s0, $f0
swc1 $f0, -8($gp)
jal main
li $v0, 10
syscall
main:
jr $ra
nop
