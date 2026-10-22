	CODE16
|sub_08028390|
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x324]
	ADD      r4, r1, #0
	LDR      r0, [r6]
	CMP      r0, #0
	BNE      |loc_080283D6|
	LDR      r0, [pc, #0x31c]
	MOV      r3, #0x68
	LDR      r0, [r0, #4]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x30c]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080283D4|
	POP      {r4, r5, r6, pc}
|loc_080283D6|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	MOV      r1, #0xf0
	AND      r0, r1
	BEQ      |loc_08028400|
	LDR      r1, [pc, #0x2d4]
	MOV      r2, #0x11
	LSL      r2, r2, #5
	ADD      r2, r4, r2
	LDR      r1, [r1, #4]
	STRH     r0, [r2, #0x10]
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	STR      r1, [r0, #0x34]
|loc_08028400|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	MOV      r5, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1c
	BEQ      |loc_0802849E|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_08028432|
	MOV      r0, #2
	STRB     r0, [r4, #0x10]
|loc_08028432|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_0802844C|
	MOV      r0, #3
	STRB     r0, [r4, #0x10]
|loc_0802844C|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x1f
	BEQ      |loc_08028464|
	STRB     r5, [r4, #0x10]
|loc_08028464|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_0802847E|
	MOV      r0, #0
	STRB     r0, [r4, #0x10]
|loc_0802847E|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802848C|
	LDR      r1, [pc, #0x23c]
	STR      r1, [r0]
|loc_0802848C|
	ADD      r5, r0, #0
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
|loc_0802849E|
	LDR      r0, [r6]
	CMP      r0, #0
	BLE      |loc_080283D4|
	SUB      r0, #1
	STR      r0, [r6]
	POP      {r4, r5, r6, pc}
	LDRH     r0, [r1, #0x12]
	LDR      r2, [pc, #0x21c]
	ADD      r1, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x16
	LDR      r0, [r2, r0]
|unk_080284B6|
	INCBIN	baserom.gba_0x284b6_0x284b8.extracted
	ASR      r0, r0, #0xd
	ADD      r1, #0x61
	STRH     r0, [r1, #0x16]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r7, r1, #0
	MOV      r2, #0x47
	LSL      r2, r2, #3
	ADD      r7, #0xff
	ADD      r7, #0xa1
	ADD      r6, r1, r2
	ADD      r4, r1, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |loc_080285B6|
	LDR      r0, [pc, #0x1dc]
	LDR      r0, [r0]
	CMP      r0, #0
	BNE      |sub_0802851E|
	LDR      r0, [pc, #0x1d8]
	MOV      r3, #0x68
	LDR      r0, [r0, #4]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x1c8]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
