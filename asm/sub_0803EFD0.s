	CODE16
|sub_0803EFD0|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_0803F002|
	ADD      r0, r4, #0
	BL       |loc_0803EEE4|
	MOV      r5, #0
|loc_0803EFE8|
	LSL      r0, r5, #1
	ADD      r0, r0, r5
	LSL      r0, r0, #5
	ADD      r0, r0, r4
	ADD      r0, #0x18
	BL       |loc_0803EE84|
	ADD      r5, #1
	CMP      r5, #0xf
	BLT      |loc_0803EFE8|
	LDRB     r0, [r4, #3]
	STRB     r0, [r4]
	B        |loc_0803F02C|
|loc_0803F002|
	MOV      r5, #0
|loc_0803F004|
	LSL      r0, r5, #1
	ADD      r0, r0, r5
	LSL      r0, r0, #5
	ADD      r0, r0, r4
	ADD      r0, #0x18
	MOV      r1, #0x4a
	LDRB     r2, [r1, r0]
	LSL      r1, r2, #0x1e
	LSR      r1, r1, #0x1e
	BEQ      |loc_0803F026|
	CMP      r1, #1
	BNE      |loc_0803F020|
	LSL      r1, r2, #0x1d
	BPL      |loc_0803F026|
|loc_0803F020|
	LDR      r1, [r0, #0x54]
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0803F026|
	ADD      r5, #1
	CMP      r5, #0xf
	BLT      |loc_0803F004|
|loc_0803F02C|
	MOV      r5, #0
|loc_0803F02E|
	LSL      r0, r5, #1
	ADD      r0, r0, r5
	LSL      r0, r0, #5
	ADD      r0, r0, r4
	ADD      r0, #0x18
	BL       |loc_0803E0B6|
	ADD      r5, #1
	CMP      r5, #0xf
	BLT      |loc_0803F02E|
	POP      {r3, r4, r5, pc}
|loc_0803F044|
	DCW      0x6a04
	DCW      0x087b,0xe5ad,0x0803,0xe7c5
|loc_0803F04E|
	LSR      r3, r0, #0x20
	LDR      r4, [r0, #0x48]
	LSR      r3, r7, #1
	LDR      r4, [r0, #0x10]
	LSR      r3, r7, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r5, r0, #0
	ADD      r7, r2, #0
	MOV      r4, #0
|loc_0803F062|
	LSL      r0, r4, #1
	ADD      r0, r0, r4
	LSL      r0, r0, #5
	ADD      r0, r0, r5
	ADD      r0, #0x18
	ADD      r2, r7, #0
	ADD      r1, r6, #0
	BL       |loc_0803E152|
	ADD      r4, #1
	CMP      r4, #0xf
	BLT      |loc_0803F062|
	POP      {r3, r4, r5, r6, r7, pc}
