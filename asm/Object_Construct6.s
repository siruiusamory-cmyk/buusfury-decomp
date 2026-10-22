	CODE16
|Object_Construct6|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08017174|
	MOV      r0, #0xff
	ADD      r0, #0x2d
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080171A6|
|loc_08017174|
	LDR      r1, [pc, #0x358]
	MOV      r2, #0
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r2, [r1, #0xc]
	STR      r2, [r1, #8]
	LDR      r3, [pc, #0x34c]
	STR      r2, [r1, #0x10]
	STR      r3, [r0]
	STR      r2, [r1, #0x20]
	STR      r4, [r1, #0x14]
	MOV      r3, #0x68
	STR      r2, [r1, #0x1c]
	LDR      r2, [pc, #0x340]
	MUL      r3, r4
	LDR      r2, [r2, #0xc]
	ADD      r2, r3, r2
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r2, r2, r3
	LDRB     r2, [r2, #0xc]
	STR      r2, [r1, #0x18]
|loc_080171A6|
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x330]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x32c]
	LDR      r5, [r5, #0x5c]
	LDR      r7, [r0, #0x68]
	SUB      sp, #0x14
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x84
	STR      r2, [sp]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x2fc]
	MOV      r1, #0
	LDR      r2, [r6, #8]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r5, #0
	LDR      r0, [r6, #8]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r5, r0, #0
	MOV      r1, #1
	ADD      r5, #0x1e
	MOV      r2, #0x84
	STR      r2, [sp]
	ADD      r3, r5, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r6, #8]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	ADD      r2, r5, #0
	ADD      r2, #0x10
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r7, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	LDR      r0, [r5, #0x18]
	CMP      r0, #2
	BLE      |loc_080172A8|
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x28
	MOV      r1, #0
	MOV      r7, #0xd4
	ADD      r3, r7, #0
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #2
	STR      r0, [sp, #4]
	MOV      r2, #2
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	STR      r0, [r5, #0x24]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x70
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #3
	ADD      r3, r7, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r2, #3
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	STR      r0, [r5, #0x28]
	LDR      r1, [r5, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r0, r4, #0
	LDR      r1, [r5, #0x28]
	BL       |inc_0x0158_0x143f2| + 0x64f6
|loc_080172A8|
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #8
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #6
	STR      r0, [sp, #4]
	MOV      r2, #6
	ADD      r1, r4, #0
	MOV      r3, #8
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #8
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #7
	STR      r0, [sp, #4]
	MOV      r2, #7
	ADD      r1, r4, #0
	MOV      r3, #0xd0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r5, [pc, #0x1e8]
	MOV      r1, #0
	LDR      r3, [r5, #0x78]
	LDR      r2, [r6, #8]
	STR      r3, [sp]
	MOV      r7, #0x14
	ADD      r3, r7, #0
	STR      r1, [sp, #8]
	MOV      r0, #2
	STR      r2, [sp, #0xc]
	MOV      r2, #0x22
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0x84
	LDR      r3, [r5, r0]
	LDR      r2, [r6, #8]
	MOV      r1, #2
	STR      r3, [sp]
	ADD      r3, r7, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	MOV      r2, #0xce
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_08016208|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_08017350|
|unk_08017350|
		PUSH {r4, r5, r6, r7, lr}
		SUB sp, #0x15c
		ADD r6, sp, #0x128
		ADD r4, r0, #0
		MOV r2, #0xa0
		MOV r1, #0xf0
		ADD r0, r6, #0
		BL       |loc_0803F540|
		MOV r5, #1
		ADD r3, r5, #0
		MOV r2, #0x1c
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |loc_08006718|
		LDR r7, [pc, #0x164]
		ADD r4, #0xff
		ADD r4, #1
		LDR r0, [r7, #0xc]
		LDR r1, [r4, #0x14]
		MOV r3, #0x68
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r2, r0, r1
		STR r2, [sp, #0x124]
		LDR r0, [r4, #0x20]
		LDR r3, [r4, #0x1c]
		ADD r1, r0, #0
		BIC r1, r5
		ADD r2, r1, #0
		SUB r1, #4
		CMP r3, r1
		BGE      |loc_0801739A|
		STR r1, [r4, #0x1c]
|loc_0801739A|
		LDR r1, [r4, #0x1c]
		CMP r1, r0
		BLE      |loc_080173A2|
		STR r2, [r4, #0x1c]
|loc_080173A2|
		LDR r2, [r4, #0x1c]
		MOV r1, #0
		CMP r2, #0
		BGE      |loc_080173AC|
		STR r1, [r4, #0x1c]
|loc_080173AC|
		LDR r1, [r4, #0x18]
		CMP r1, #2
		BLE      |inc_0x153f2_0x1a3f2| + 0x200c
		ADD r1, r5, #0
		CMP r0, #2
		LDR r2, [r4, #0x24]
		BGE      |loc_080173BC|
		MOV r1, #0
|loc_080173BC|
		STR r1, [r2, #8]
		LDR r1, [r4, #0x20]
		LDR r0, [r4, #0x28]
		LDR r2, [r4, #0x18]
		LSR r1, r1, #1
		SUB r2, #1
		LSR r2, r2, #1
		LSL r2, r2, #1
		LSL r1, r1, #1
		CMP r1, r2
		BGE      |sub_080173D6|
		MOV r1, #1
		B        |inc_0x153f2_0x1a3f2| + 0x1fe6
