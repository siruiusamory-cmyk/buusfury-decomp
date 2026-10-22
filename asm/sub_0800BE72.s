	CODE16
|sub_0800BE72|
	LSR      r7, r0, #0x20
	MOV      r4, #0x10
	LSR      r7, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	STMIA    r0!, {r4, r5, r6}
	LSR      r4, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
