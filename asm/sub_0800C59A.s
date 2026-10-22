	CODE16
|sub_0800C59A|
	LSL      r0, r0, #0
	MOV      r5, #0
	LSR      r7, r0, #0x20
	SUB      r0, r7, r3
	LSL      r0, r0, #0xc
	LDR      r7, [sp, #0xe0]
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	LDR      r2, [r0, #0x2c]
	LDR      r0, [pc, #0x27c]
	LDR      r0, [r0]
	BL       |loc_080119BC|
	MOV      r0, #0
	STR      r0, [r4, #0x2c]
	ADD      r0, r4, #0
	BEQ      |loc_0800C5CC|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800C5CC|
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [r0, #0x28]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x258]
	ADD      r5, r4, #0
	LDR      r7, [r0, #4]
	ADD      r5, #0x14
	ADD      r7, #0x80
	MOV      r2, #1
	ADD      r0, r5, #0
	LDR      r1, [r7, #0x28]
	BL       |loc_08009930|
	MOV      r2, #1
	ADD      r0, r5, #0
	LDR      r1, [r7, #0x30]
	BL       |loc_08009930|
	LDR      r0, [pc, #0x23c]
	LDR      r2, [r4, #0x2c]
	LDR      r0, [r0]
	ADD      r1, r4, #0
	BL       |loc_080119BC|
	MOV      r0, #0
	STR      r0, [r4, #0x2c]
	ADD      r0, r4, #0
	BEQ      |loc_0800C612|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800C612|
	ADD      r0, r6, #0
	ADD      r0, #8
	LDR      r1, [r6, #8]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, r6, r7, pc}
	LDR      r0, [r0, #0x10]
	LDR      r1, [pc, #0x210]
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BX       lr
|sub_0800C628|
|unk_0800C628|
		LDR r1, [r0, #8]
		SUB sp, #8
		LDR r2, [r1, #0x14]
		LDR r3, [r1, #0x1c]
		LDR r1, [r1, #0x20]
		ADD r2, r2, r3
		STR r1, [sp, #4]
		LDR r1, [pc, #0x200]
		ASR r2, r2, #1
		STR r2, [sp]
		LDR r3, [sp, #4]
		STMIA r1!, {r2, r3}
		LDR r1, [r0, #8]
		LDR r2, [pc, #0x1f0]
		LDR r1, [r1, #0x10]
		LDR r3, [pc, #0x1f4]
		LSL r1, r1, #3
		ADD r1, r1, r2
		LDR r2, [r1]
		LDR r1, [r1, #4]
		LSL r2, r2, #8
		LSL r1, r1, #8
		STR r1, [r3, #4]
		STR r2, [r3]
		LDR r0, [r0, #8]
		ADD sp, #8
		B        |inc_0x0158_0x143f2| + 0xc476
