	CODE16
|sub_0801ED06|
	SUB      r1, r2, #3
	CMP      r1, #5
	BCS      |loc_0801ED22|
	ADD      r3, pc, #0x4
	LDRB     r3, [r3, r1]
	LSL      r3, r3, #1
	ADD      pc, r3
|loc_0801ED14|
	LSL      r2, r0, #0x18
	LSL      r6, r0, #0x18
	LSL      r7, r0, #0
	MOV      r1, #1
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r1, [r0, #0x2c]
|loc_0801ED22|
	BX       lr
	MOV      r1, #1
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r1, [r0, #0x2c]
	BX       lr
	LSL      r0, r0, #0
	LSR      r0, r6, #0x1f
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x324]
	SUB      sp, #0x14
	LDR      r1, [r0, #0x68]
	LDR      r5, [r0, #0x5c]
	STR      r1, [sp, #0x10]
	MOV      r1, #0xff
	ADD      r1, #0x4d
	LDR      r7, [r0, r1]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x36
	STR      r2, [sp]
	MOV      r1, #1
	MOV      r0, #0
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x2f8]
	MOV      r1, #0
	LDR      r2, [r6, #4]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x42
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r5, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r5, r0, #0
	MOV      r1, #1
	ADD      r5, #0x1e
	MOV      r2, #0x36
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
	LDR      r2, [r6, #4]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x10]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r5, #0
	ADD      r2, #0x10
	MOV      r0, #5
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x42
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r6, #4]
	MOV      r1, #0
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x10
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x1c
	MOV      r0, #0
	STR      r7, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x24
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #4
	STR      r0, [sp, #4]
	MOV      r2, #4
	ADD      r1, r4, #0
	MOV      r3, #0x24
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	STR      r0, [r5, #0x30]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x24
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #5
	STR      r0, [sp, #4]
	MOV      r2, #5
	ADD      r1, r4, #0
	MOV      r3, #0x56
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r0, [r5, #0x34]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x208]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x55
	LSL      r2, r2, #7
	MOV      r1, #0
	LDR      r0, [pc, #0x200]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #7
	STR      r0, [sp]
	MOV      r0, #6
	STR      r0, [sp, #4]
	MOV      r0, #0x18
	STR      r0, [sp, #8]
	MOV      r0, #0x10
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	LDR      r2, [pc, #0x1ec]
	LDR      r1, [pc, #0x1e4]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x1e8]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #8]
	LDRH     r1, [r0]
	LSR      r2, r0, #0x12
	ORR      r1, r2
	STRH     r1, [r0]
	MOV      r0, #0
	STR      r0, [r5, #0x28]
	MOV      r1, #1
	STR      r1, [r5, #0x1c]
	STR      r0, [r5, #0x2c]
	ADD      r5, #0x20
	STMIA    r5!, {r0, r1}
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1a
	LDRH     r1, [r3]
	LSR      r2, r3, #0x12
	BIC      r1, r2
	STRH     r1, [r3]
	CMP      r0, #0
	BEQ      |loc_0801EEC8|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801EEC8|
	POP      {r3, pc}
|sub_0801EECA|
|unk_0801EECA|
		PUSH {r4, r5, r6, r7, lr}
		SUB sp, #0x34
		ADD r5, r0, #0
		MOV r2, #0x50
		MOV r1, #0x88
		MOV r0, sp
		MOV r6, sp
		BL       |loc_0803F540|
		ADD r0, r6, #0
		BL       |inc_0x0158_0x143f2| + 0x4f3e
		ADD r4, r5, #0
		ADD r4, #0xff
		ADD r4, #1
		LDR r1, [r4, #0x30]
		LDR r2, [r4, #0x1c]
		MOV r7, #1
		ADD r0, r7, #0
		CMP r2, #0
		BGT      |loc_0801EEF6|
		MOV r0, #0
|loc_0801EEF6|
		STR r0, [r1, #8]
		LDR r1, [r4, #0x14]
		LDR r0, [pc, #0x17c]
		LDR r2, [r4, #0x34]
		LDR r3, [r4, #0x1c]
		CMP r1, r0
		BHS      |loc_0801EF06|
		ADD r0, r1, #0
|loc_0801EF06|
		CMP r3, r0
		BHS      |sub_0801EF0E|
		MOV r0, #1
		DCW     0xE000
