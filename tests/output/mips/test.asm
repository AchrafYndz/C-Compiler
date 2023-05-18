.data:
    victory_msg: .asciiz "You won!"

main:                                   # @main
        addiu   $sp, $sp, -32
        sw      $ra, 28($sp)                    # 4-byte Folded Spill
        sw      $fp, 24($sp)                    # 4-byte Folded Spill
        move    $fp, $sp
        sw      $zero, 20($fp)

        #  c) display victory
        li $v0, 4
        la $a0, victory_msg
        syscall

        move    $sp, $fp
        lw      $fp, 24($sp)                    # 4-byte Folded Reload
        lw      $ra, 28($sp)                    # 4-byte Folded Reload
        addiu   $sp, $sp, 32
        jr      $ra
        nop