	CODE16
|sub_0803C72E|
	PUSH     {r3, lr}
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803C73E|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
|loc_0803C73E|
	POP      {r3, pc}
|loc_0803C740|
	DCW      0x1c34
	DCW      0x0300,0x268c,0x0807,0xb720
|loc_0803C74A|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r1, r0
	ADD      r4, r1, #0
	LDR      r1, [r0]
	ADD      r0, r4, #0
	SUB      sp, #0x20
	BL       |inc_0x0158_0x143f2| + 0xeca0
	LDR      r5, [pc, #0xb0]
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0803C7BE|
	ADD      r1, r4, #0
	ADD      r0, sp, #8
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #8]
	LDR      r2, [sp, #0x10]
	LDR      r3, [sp, #0x14]
	ADD      r2, r0, r2
	STR      r2, [sp]
	ASR      r2, r2, #1
	LDR      r0, [sp, #0xc]
	STR      r2, [sp]
	ADD      r0, r0, r3
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	STR      r2, [sp, #0x18]
	MOV      r2, #0x37
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x1c]
	MOV      r0, #0
	ADD      r1, sp, #0x18
|loc_0803C79C|
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #0x45
	LDR      r2, [pc, #0x6c]
	LSL      r1, r1, #3
	LDR      r0, [r5]
	LDR      r5, [pc, #0x68]
	ADD      r1, r1, r2
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r5
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0803C7BE|
	LDR      r0, [pc, #0x60]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_0803C7F6|
	LDRB     r1, [r6, #4]
	CMP      r1, #0
	BEQ      |loc_0803C7F6|
	STR      r0, [sp, #0x10]
	LDRB     r0, [r0, #0x10]
	ADD      r3, sp, #0
	ADD      r5, sp, #4
	STRB     r0, [r3, #4]
	LDR      r0, [pc, #0x4c]
	ADD      r1, r5, #0
	STR      r0, [sp, #0xc]
	MOV      r0, #1
	LSL      r0, r0, #0xc
	STR      r0, [sp, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xe880
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x58]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803C7F6|
	ADD      sp, #0x20
	POP      {r4, r5, r6, pc}
|sub_0803C7FA|
|unk_0803C7FA|
		MOV r0, #1
		BX       lr
