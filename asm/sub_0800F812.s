	CODE16
|sub_0800F812|
	PUSH     {r3, r4, r5, lr}
	LDR      r0, [r0, #0x24]
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_0800F864|
	LDR      r2, [pc, #0xe4]
	MOV      r3, #0x68
	LDR      r0, [r2, #4]
	LDRB     r4, [r0]
	MUL      r3, r4
	ADD      r0, r3, r0
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r0, r0, r3
	MOV      r3, #0x58
	LDRSH    r0, [r0, r3]
	MUL      r0, r1
	ADD      r0, #0xff
	ASR      r4, r0, #8
	BEQ      |loc_0800F864|
	MOV      r0, #0xc
	LDR      r5, [r2]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800F850|
	MOV      r1, #1
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0xcc]
	STR      r1, [r0]
	STR      r4, [r0, #8]
|loc_0800F850|
	ADD      r2, r0, #0
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r0, r5, r0
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
|loc_0800F864|
	POP      {r3, r4, r5, pc}
|sub_0800F866|
|unk_0800F866|
		PUSH {r0, r1, r2, r4, r5, r6, r7, lr}
		ADD r5, r2, #0
		ADD r4, r0, #0
		ADD r1, r0, #0
		SUB sp, #0x20
		ADD r0, sp, #0x10
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0x10]
		LDR r1, [sp, #0x18]
		LDR r7, [sp, #0x1c]
		ADD r0, r0, r1
		ASR r6, r0, #1
		CMP r5, #0
		BEQ      |sub_0800F89A|
		LDRB r0, [r5]
		LDR r1, [pc, #0x94]
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [r0]
		LDR r0, [r0, #4]
		LSL r1, r1, #8
		LSL r0, r0, #8
		STR r0, [sp, #0xc]
		STR r1, [sp, #8]
		B        |inc_0x0158_0x143f2| + 0xf748
