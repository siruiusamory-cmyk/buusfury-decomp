	CODE16
|loc_080176D6|
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x1fc
	MOV      r2, #0xff
	ADD      r2, #1
	SUB      sp, #0x1fc
	SUB      sp, #0xc
	CMP      r1, r2
	BLE      |loc_080176EA|
	ADD      r1, r2, #0
	B        |loc_080176F0|
|loc_080176EA|
	CMP      r1, #0
	BGE      |loc_080176F0|
	MOV      r1, #0
|loc_080176F0|
	MOV      r2, #0
	MOV      r4, #1
	LSL      r4, r4, #9
|loc_080176F6|
	LSL      r5, r2, #1
	ADD      r3, r5, r0
	LDRH     r4, [r3, #4]
	ADD      r2, #1
	LSL      r3, r4, #0x16
	LSR      r7, r3, #0x1b
	LSL      r6, r4, #0x1b
	LSL      r3, r4, #0x11
	LSR      r4, r3, #0x1b
	LSR      r6, r6, #0x1b
	MUL      r7, r1
	ASR      r7, r7, #8
	MUL      r6, r1
	MUL      r4, r1
	ASR      r4, r4, #8
	ASR      r6, r6, #8
	LSL      r7, r7, #5
	ORR      r6, r7
	LSL      r3, r4, #0xa
	ORR      r6, r3
	ADD      r4, r6, #0
	ADD      r3, sp, #4
	STRH     r4, [r3, r5]
	MOV      r4, #1
	LSL      r4, r4, #9
	CMP      r2, r4
	BLT      |loc_080176F6|
	ADD      r2, r4, #0
	ADD      r5, sp, #4
	ADD      r1, r5, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r1, r5, r4
	ADD      r2, r4, #0
	LDR      r0, [pc, #0x184]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
