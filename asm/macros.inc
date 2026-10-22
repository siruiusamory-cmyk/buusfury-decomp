
        MACRO
        thumb_func_start $name
        EXPORT  $name
        CODE16
$name   PROC
        MEND

        MACRO
        thumb_func_end $name
        ENDP
        MEND

        MACRO
        arm_func_start $name
        EXPORT  $name
        CODE32
$name   PROC
        MEND

        MACRO
        arm_func_end $name
        ENDP
        MEND

        END
