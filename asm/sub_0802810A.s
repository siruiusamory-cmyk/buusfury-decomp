	CODE16
|sub_0802810A|
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	DCW      0xea60,0x0874
	LDRB     r1, [r6, #0x1a]
	LSR      r2, r0, #0x20
	ASR      r0, r3, #0x1d
	LSR      r7, r0, #0x20
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	LDRB     r7, [r5, #0x1b]
	LSR      r2, r0, #0x20
	LDRB     r5, [r6, #0x1d]
	LSR      r2, r0, #0x20
	LDRB     r1, [r7, #0x1e]
	LSR      r2, r0, #0x20
	LDR      r1, [r0, #0x14]
	ADD      r1, #1
	STR      r1, [r0, #0x14]
	CMP      r1, #8
	BLT      |loc_08028142|
	LDR      r1, [pc, #0x230]
	STR      r1, [r0, #0x30]
	MOV      r1, #0
	STR      r1, [r0, #0x18]
	MOV      r1, #1
	STR      r1, [r0, #0x1c]
|loc_08028142|
	BX       lr
|loc_08028144|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0802815C|
	MOV      r0, #0x9c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802815C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
