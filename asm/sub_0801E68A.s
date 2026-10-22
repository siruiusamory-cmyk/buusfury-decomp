	CODE16
|sub_0801E68A|
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0xbc]
	SUB      r4, #0x14
	LDR      r0, [r4]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BEQ      |loc_0801E6D6|
	BL       |inc_0x03d784_0x041118| + 0x2954
	LDR      r0, [r4, #4]
	MOV      r4, #0
	LDR      r5, [pc, #0xb4]
	ADD      r3, r4, #0
	MOV      r2, #0x40
	ADD      r0, r0, r5
	LDR      r1, [pc, #0xb0]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #0xff
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801E6D2|
	LDR      r1, [pc, #0xa0]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	STR      r4, [r1, #0x10]
	LDR      r1, [pc, #0x9c]
	STR      r1, [r0]
|loc_0801E6D2|
	BL       |inc_0x03d784_0x041118| + 0xcc
|loc_0801E6D6|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	PUSH     {r3, lr}
	LDR      r2, [r1, #0x14]
	LDR      r2, [r2, #0x30]
	CMP      r2, #0
	BNE      |loc_0801E6F6|
	LDR      r2, [r1, #0xc]
	CMP      r2, #1
	BNE      |loc_0801E6F6|
	MOV      r2, #0
	STR      r2, [r1, #0xc]
	STR      r2, [r1, #0x10]
|loc_0801E6F6|
	BL       |inc_0x0158_0x143f2| + 0x667e
	POP      {r3, pc}
|sub_0801E6FC|
|unk_0801E6FC|
		ADD r2, r0, #0
		ADD r0, r1, #0
		MOV r1, #1
		PUSH {r4, lr}
		STRB r1, [r0]
		STRB r1, [r0, #2]
		LDR r1, [pc, #0x64]
		STR r1, [r0, #0x20]
		LDR r1, [r2, #4]
		ADD r1, #0xff
		ADD r1, #1
		LDR r1, [r1, #0xc]
		LDR r3, [r2, #8]
		CMP r1, r3
		BNE      |sub_0801E71E|
		MOV r1, #6
		B        |loc_0801E728|
