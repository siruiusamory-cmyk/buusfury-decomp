	CODE16
|sub_08018078|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x24]
	MOV      r1, #0x4b
	ADD      r0, #1
	LSL      r1, r1, #3
	CMP      r0, r1
	STR      r0, [r4, #0x24]
	BLE      |loc_0801809C|
	LDR      r5, [pc, #0x1dc]
	LDR      r1, [r4, #0x68]
	LDR      r0, [r5, #0x10]
	BL       |inc_0x0158_0x143f2| + 0x12532
	ADD      r1, r4, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0801809C|
	POP      {r3, r4, r5, pc}
|sub_0801809E|
|unk_0801809E|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		ADD r6, r4, #0
		ADD r5, r4, #0
		LDR r0, [r0, #0x2c]
		ADD r5, #0x14
		ADD r6, #0x30
		MOV r1, #0
		CMP r0, #0x3c
		SUB sp, #0x44
		BGE      |loc_08018198|
		ADD r0, #1
		ADD r2, r4, #0
		ADD r2, #0x50
		STR r0, [r4, #0x2c]
		STR r2, [sp, #0x40]
		LDR r1, [r4, #0x50]
		LDR r3, [r4, #0x58]
		ADD r2, #4
		STR r2, [sp, #0x3c]
		LDR r2, [r2]
		LDR r0, [r4, #0x5c]
		ADD r1, r1, r3
		ADD r0, r2, r0
		STR r0, [sp, #0x28]
		ADD r0, r1, #0
		STR r1, [sp, #0x24]
		LDR r1, [sp, #0x28]
		STR r0, [sp, #0x2c]
		STR r1, [sp, #0x30]
		STR r1, [sp, #0x38]
		ASR r1, r0, #8
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x38]
		STR r1, [sp, #0x24]
		ASR r0, r0, #8
		STR r0, [sp, #0x28]
		STR r0, [sp, #0x30]
		ADD r0, r1, #0
		STR r1, [sp, #0x2c]
		LDR r1, [r4, #0x48]
		CMP r0, r1
		BNE      |loc_080180FC|
		LDR r0, [sp, #0x30]
		LDR r1, [r4, #0x4c]
		CMP r0, r1
		BEQ      |loc_080181BA|
|loc_080180FC|
		LDR r0, [sp, #0x2c]
		LDR r1, [r4, #0x48]
		SUB r0, r0, r1
		LDR r1, [sp, #0x30]
		LDR r2, [r4, #0x4c]
		STR r0, [sp, #0x14]
		SUB r1, r1, r2
		STR r1, [sp, #0x18]
		LDR r2, [sp, #0x18]
		ADD r1, r0, #0
		LDR r0, [r5]
		LDR r3, [r5, #4]
		ADD r0, r0, r1
		ADD r3, r3, r2
		STR r3, [sp, #8]
		STR r0, [sp, #4]
		ADD r7, r0, #0
		LDR r0, [sp, #8]
		LDR r3, [r5, #8]
		MOV ip, r0
		LDR r0, [r5, #0xc]
		ADD r1, r3, r1
		ADD r0, r0, r2
		ADD r2, r0, #0
		STR r0, [sp, #8]
		MOV r0, ip
		STR r0, [sp, #0x10]
		STR r7, [sp, #0xc]
		ADD r0, sp, #0xc
		STR r2, [sp, #0x18]
		STR r1, [sp, #4]
		STR r1, [sp, #0x14]
		LDMIA r0!, {r0, r1, r2, r3}
		ADD r7, sp, #0x1c
		STMIA r7!, {r0, r1, r2, r3}
		LDR r0, [pc, #0x124]
		SUB r7, #0x10
		LDR r0, [r0, #0xc]
		ADD r0, #0x80
		LDR r1, [r0, #0x28]
		ADD r0, sp, #0x1c
		BL       |loc_08009324|
		CMP r0, #0
		BEQ      |loc_080181BA|
		LDR r0, [sp, #0x34]
		LDR r2, [sp, #0x40]
		STR r0, [r2]
		ADD r2, sp, #0x38
		LDMIA r2!, {r0, r2}
		STR r0, [r2]
		ADD r2, sp, #0x2c
		LDMIA r2!, {r1, r2}
		STR r1, [r4, #0x48]
		STR r2, [r4, #0x4c]
		LDR r1, [sp, #0x2c]
		LDR r0, [r4, #0x60]
		LDRB r2, [r0]
		LSR r2, r2, #1
		SUB r1, r1, r2
		STR r1, [r4, #0x38]
		LDRB r0, [r0]
		ADD r0, r1, r0
		STR r0, [r4, #0x40]
		LDR r0, [sp, #0x30]
		STR r0, [r4, #4]
		LDMIA r7!, {r0, r1, r2, r3}
		STMIA r5!, {r0, r1, r2, r3}
		LDR r0, [r4, #0x68]
		LDR r2, [r4, #0x14]
		LDR r3, [r4, #0x18]
		LDR r7, [r4, #0x1c]
		SUB r5, #0x10
		SUB r2, #4
		SUB r3, #4
		ADD r7, #4
		MOV ip, r7
		B        |loc_0801819A|
|loc_08018198|
		B        |sub_080181D4|
|loc_0801819A|
		LDR r7, [r4, #0x20]
		ADD r1, r2, #0
		ADD r7, #4
		STR r7, [sp, #0x18]
		MOV r7, ip
		SUB r1, #0xf
		STR r2, [sp, #0xc]
		STR r7, [sp, #0x14]
		STR r3, [sp, #0x10]
		LDR r7, [sp, #0x18]
		SUB r2, r3, #7
		STRH r1, [r0, #4]
		STRH r2, [r0, #6]
		MOV r3, ip
		STRH r3, [r0, #8]
		STRH r7, [r0, #0xa]
|loc_080181BA|
		LDR r0, [r4, #0x34]
		SUB r0, #4
		STR r0, [r4, #0x34]
		LDR r1, [r4, #0x30]
		ADD r0, r1, r0
		STR r0, [r4, #0x30]
		CMP r0, #0
		BGT      |inc_0x153f2_0x1a3f2| + 0x2de4
		NEG r0, r0
		STR r0, [r6]
		MOV r0, #0x80
		STR r0, [r4, #0x34]
		B        |inc_0x153f2_0x1a3f2| + 0x2de4
