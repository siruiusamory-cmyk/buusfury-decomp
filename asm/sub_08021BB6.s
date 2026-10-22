	CODE16
|sub_08021BB6|
	LSL      r0, r0, #0xc
	ADD      r6, pc, #0x2D0
	LSR      r2, r6, #1
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0
	DCW      0xf000,0x0600
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	LDR      r2, [pc, #0x170]
	LSL      r0, r0, #0xc
	LDR      r2, [pc, #0x180]
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	ADD      r0, r0, #1
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	ADD      r0, sp, #0x2b0
	LSR      r4, r0, #0x20
	STR      r4, [sp, #0x90]
	LSR      r4, r0, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r6, [sp, #0x330]
	LSR      r4, r0, #0x20
|loc_08021BF8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	BNE      |sub_08021C0C|
	MOV      r0, #4
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08021C0C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
