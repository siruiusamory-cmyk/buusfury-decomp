	CODE16
|sub_08017BF2|
	LSL      r0, r0, #0x18
	ADD      r3, pc, #0x260
	LSR      r7, r5, #1
	STRH     r0, [r0, #4]
	LSL      r0, r0, #0x18
	LSR      r3, r0, #0x1e
	LSL      r0, r0, #0
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	LSR      r4, r0, #1
	LSL      r0, r0, #0
	LSL      r3, r2, #1
	LSL      r0, r0, #0x10
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r2, #1
	LSL      r0, r0, #0x10
	ADD      r3, sp, #0x3d0
	LSR      r7, r5, #1
	LDR      r3, [pc, #0x200]
	LSL      r0, r0, #0x18
