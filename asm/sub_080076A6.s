	CODE16
|sub_080076A6|
	LSL      r0, r0, #0
	ADR      r0, |loc_0800791C|
	LSR      r4, r0, #0x20
	LSL      r0, r3, #0x1f
	LSR      r7, r0, #0x20
	STR      r5, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	LDR      r2, [r0, #0x10]
	LDR      r0, [pc, #0x30]
	MOV      r1, #0x17
	LDR      r0, [r0]
	BL       |loc_08011C0C|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080076D6|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
