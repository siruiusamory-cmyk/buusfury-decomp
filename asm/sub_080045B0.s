	CODE16
|sub_080045B0|
|unk_080045B0|
		ADD r4, #1
		CMP r6, r4
		BGT      |inc_0x0158_0x143f2| + 0x441c
|loc_080045B6|
|unk_080045B6|
		MOV r2, #0xff
		LDR r0, [pc, #0x254]
		ADD r2, #8
		MOV r3, #0
		ADD r0, #0x10
		ADR      r1, |inc_0x0158_0x143f2| + 0x46c0
	INCBIN  baserom.gba_0x45c2_0x45c4.extracted
|sub_080045C4|
|unk_080045C4|
	INCBIN	baserom.gba_0x45c4_0x45c8.extracted
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	ADD      r5, r0, #0
	LDR      r0, [sp, #0x10]
|loc_080045D0|
	ADD      r4, r3, #0
	MOV      r3, #0x68
	MUL      r0, r3
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r5
	ADD      r1, r0, r1
	MOV      r0, #0x2c
	STR      r1, [sp, #4]
	LDR      r1, [pc, #0x230]
	MUL      r0, r4
	ADD      r6, r0, r1
	ADD      r1, r5, #0
	ADD      r7, r2, #0
	LSL      r0, r7, #2
	ADD      r1, #0xe4
	ADD      r0, r0, r1
	ADD      r0, #4
	STR      r0, [sp, #8]
	ADD      r3, r7, #1
	BEQ      |loc_0800460E|
	LDR      r0, [sp, #8]
	LDR      r0, [r0]
	LSR      r1, r0, #0x1c
	BEQ      |loc_0800460E|
	LSR      r1, r0, #0x1c
	SUB      r1, #1
	ADD      r0, r5, #0
	LDRB     r2, [r6, #0x14]
	BL       |loc_08004544|
|loc_0800460E|
	LDRB     r2, [r6, #0x14]
	LDR      r1, [sp, #4]
	LSL      r0, r2, #2
	ADD      r1, r0, r1
	ADD      r1, #0x3c
	LDR      r1, [r1]
	LDR      r3, [pc, #0x1f4]
	LDR      r0, [r3, r0]
	CMP      r1, r0
	BEQ      |loc_0800462A|
	ADD      r0, r5, #0
	LDR      r1, [sp, #0x10]
	BL       |loc_08004544|
|loc_0800462A|
	LDRB     r0, [r6, #0x14]
	LDR      r1, [sp, #4]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	ADD      r0, #0x3c
|loc_08004634|
	STR      r4, [r0]
	LDR      r1, [r0]
	CMP      r1, r4
	BNE      |loc_08004634|
	ADD      r3, r7, #1
	BEQ      |loc_08004652|
	LDR      r0, [sp, #8]
	LDR      r1, [r0]
	LDR      r2, [sp, #0x10]
	LSL      r1, r1, #4
	LSR      r1, r1, #4
	ADD      r2, #1
	LSL      r2, r2, #0x1c
	ORR      r1, r2
	STR      r1, [r0]
|loc_08004652|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r2, r0, #0
	LSL      r0, r1, #2
	ADD      r5, #0xe4
	ADD      r0, r0, r5
	ADD      r7, r0, #0
	ADD      r0, #4
	LDR      r4, [r0]
	LSR      r3, r4, #0x1c
	BEQ      |loc_08004698|
	LSL      r6, r4, #4
	LSR      r6, r6, #4
	MOV      r3, #0x2c
	MUL      r3, r6
	LDR      r6, [pc, #0x19c]
	LSR      r4, r4, #0x1c
	ADD      r6, r3, r6
	MOV      r3, #0x68
	SUB      r4, #1
	MUL      r3, r4
	ADD      r2, r3, r2
	LDRB     r3, [r6, #0x14]
	LDR      r4, [pc, #0x1a8]
	LSL      r3, r3, #2
	ADD      r2, r2, r3
	ADD      r2, r2, r4
	LDR      r4, [pc, #0x180]
	LDR      r3, [r4, r3]
|loc_08004690|
	STR      r3, [r2]
	LDR      r4, [r2]
	CMP      r4, r3
	BNE      |loc_08004690|
|loc_08004698|
	LDR      r2, [r5]
	SUB      r2, #1
	STR      r2, [r5]
	SUB      r1, r2, r1
	BEQ      |loc_080046AC|
	LSL      r2, r1, #2
	ADD      r1, r7, #0
	ADD      r1, #8
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080046AC|
	POP      {r3, r4, r5, r6, r7, pc}
