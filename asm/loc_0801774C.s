	CODE16
|loc_0801774C|
	PUSH     {r4, r5, r6, r7, lr}
	MOV      ip, r0
	MOV      r0, #0xff
	SUB      sp, #0x1fc
	SUB      sp, #0x1fc
	ADD      r0, #1
	CMP      r1, r0
	SUB      sp, #0xc
	BLE      |loc_08017762|
	ADD      r1, r0, #0
	B        |loc_08017768|
|loc_08017762|
	CMP      r1, #0
	BGE      |loc_08017768|
	MOV      r1, #0
|loc_08017768|
	LSL      r2, r1, #5
	SUB      r2, r2, r1
	SUB      r1, r0, r1
	MOV      r0, #0
	MOV      r4, #1
	LSL      r4, r4, #9
|loc_08017774|
	LSL      r5, r0, #1
	ADD      r3, r5, #0
	ADD      r3, ip
	LDRH     r4, [r3, #4]
	ADD      r0, #1
	LSL      r3, r4, #0x16
	LSR      r7, r3, #0x1b
	LSL      r6, r4, #0x1b
	LSL      r3, r4, #0x11
	LSR      r4, r3, #0x1b
	LSR      r6, r6, #0x1b
	MUL      r6, r1
	ADD      r3, r6, r2
	ASR      r6, r3, #8
	MUL      r7, r1
	ADD      r3, r7, r2
	ASR      r7, r3, #8
	MUL      r4, r1
	ADD      r3, r4, r2
	ASR      r4, r3, #8
	LSL      r7, r7, #5
	ORR      r6, r7
	LSL      r3, r4, #0xa
	ORR      r6, r3
	ADD      r4, r6, #0
	ADD      r3, sp, #4
	STRH     r4, [r3, r5]
	MOV      r4, #1
	LSL      r4, r4, #9
	CMP      r0, r4
	BLT      |loc_08017774|
	ADD      r2, r4, #0
	ADD      r5, sp, #4
	ADD      r1, r5, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r1, r5, r4
	ADD      r2, r4, #0
	LDR      r0, [pc, #0xfc]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #1
	LSL      r0, r0, #0xa
	ADD      r4, r5, r0
	LDR      r0, [r4, #4]
	ADD      r0, #1
	LSL      r1, r0, #8
	STR      r0, [r4, #4]
	LDR      r0, [r4, #8]
	BL       |inc_0x046118_0x049114| + 0xd40
	MOV      r1, #0xff
	ADD      r1, #1
	SUB      r1, r1, r0
	ADD      r0, r5, #0
	BL       |loc_080176D6|
	ADD      r1, r4, #4
	LDMIA    r1!, {r0, r1}
	CMP      r0, r1
	BLT      |sub_08017802|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
