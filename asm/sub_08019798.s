	CODE16
|sub_08019798|
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	STR      r6, [sp, #0x380]
	LSR      r1, r6, #1
	LDMIA    r6!, {r3, r5}
	LSR      r4, r0, #0x20
	STR      r0, [r0]
	LSL      r0, r4
	STR      r0, [r0]
	LSR      r0, r0
	LDR      r0, [sp, #0x390]
	LSR      r1, r6, #1
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
