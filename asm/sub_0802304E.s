	CODE16
|sub_0802304E|
	LSL      r1, r0, #2
	ADD      r1, r1, r5
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r2, [r1, #0x2c]
	CMP      r2, #0
	BEQ      |loc_08023078|
	ADD      r1, r2, #0
	LDR      r2, [r2, #0x58]
	ADD      r1, #0x6c
	LDRB     r3, [r2, #8]
	LDRB     r2, [r2, #9]
	LSR      r4, r3, #1
	MOV      r3, #0x2a
	MUL      r3, r0
	ADD      r3, #0x23
	SUB      r3, r3, r4
	LSR      r2, r2, #1
	SUB      r2, r6, r2
	STR      r2, [r1, #4]
	STR      r3, [r1]
|loc_08023078|
	ADD      r0, #1
	CMP      r0, #5
	BLT      |sub_0802304E|
	LDR      r0, [sp, #8]
	MOV      r1, #0
	STRB     r1, [r0]
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_08023088|
|unk_08023088|
; cited by 0x08022D74 (a pc-relative load targets 0x08023088)
	INCBIN  baserom.gba_0x23088_0x2309c.extracted
		PUSH {r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r0, [pc, #0x3e0]
		ADD r4, r5, #0
		LDR r0, [r0, #0x10]
		ADD r4, #0xff
		LDR r2, [pc, #0x3dc]
		LDRB r1, [r0]
		ADD r4, #1
		MOV r3, #1
		ADD r6, r5, r2
		CMP r1, #0
		LDR r0, [r4, #0x1c]
		SUB sp, #0x7c
		BEQ      |loc_080230CC|
		CMP r1, #1
		BNE      |loc_080230DE|
		ADD r1, r3, #0
		CMP r0, #0x1f
		LDR r2, [r4, #0x18]
		BLT      |loc_080230C8|
		MOV r1, #0
|loc_080230C8|
		STR r1, [r2, #8]
		B        |loc_080230DE|
|loc_080230CC|
		LDR r1, [r4, #0x18]
		LDR r2, [r6]
		SUB r2, #1
		CMP r2, r0
		BLE      |loc_080230DA|
		MOV r0, #1
		B        |loc_080230DC|
|loc_080230DA|
		MOV r0, #0
|loc_080230DC|
		STR r0, [r1, #8]
|loc_080230DE|
		LDR r0, [r4, #0x14]
		LDR r2, [r4, #0x1c]
		MOV r1, #1
		CMP r2, #0
		BGT      |loc_080230EA|
		MOV r1, #0
|loc_080230EA|
		STR r1, [r0, #8]
		MOV r1, #0xf0
		MOV r2, #0xa0
		ADD r7, sp, #0x48
		ADD r0, r7, #0
		BL       |loc_0803F540|
		MOV r3, #1
		MOV r2, #0x5f
		ADD r0, r5, #0
		ADD r1, sp, #0x48
		BL       |loc_08006718|
		MOV r0, #1
		ADD r3, sp, #0x40
		STRB r0, [r3, #8]
		MOV r0, #0x78
		STR r0, [sp, #0x4c]
		MOV r0, #0x30
		STR r0, [sp, #0x50]
		LDR r0, [pc, #0x370]
		LDR r0, [r0, #0x10]
		LDRB r1, [r0]
		LDR r0, [pc, #0x370]
		CMP r1, #1
		LDR r1, [r4, #0x1c]
		DCW     0xD107
		ADD r1, #0x74
		LSL r1, r1, #2
		LDR r2, [r0, r1]
		ADR      r1, |loc_08023490|
		ADD r0, r7, #0
	INCBIN  baserom.gba_0x2312a_0x2312c.extracted
|sub_0802312C|
|unk_0802312C|
	INCBIN	baserom.gba_0x2312c_0x23130.extracted
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r1, r1, r6
	LDR      r1, [r1, #0xc]
	ADD      r1, #0x9e
	LSL      r1, r1, #2
	LDR      r2, [r0, r1]
	ADD      r1, pc, #0x34C
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	LDR      r1, [pc, #0x34c]
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r2, #0x38
	MOV      r1, #0x30
	ADD      r4, sp, #0x14
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r0, #0
	STR      r0, [sp, #4]
	STR      r0, [sp, #8]
	MOV      r0, #0x30
	STR      r0, [sp, #0xc]
	MOV      r0, #0x38
	STR      r0, [sp, #0x10]
	MOV      r2, #0
	ADD      r0, r4, #0
	ADD      r1, sp, #4
	BL       |inc_0x03d784_0x041118| + 0x21f0
	MOV      r0, #0xa
	STR      r0, [sp, #4]
	MOV      r0, #2
	STR      r0, [sp, #8]
	MOV      r0, #0x25
	STR      r0, [sp, #0xc]
	MOV      r0, #0x2c
	STR      r0, [sp, #0x10]
	ADD      r0, r4, #0
	ADD      r1, sp, #4
	BL       |inc_0x0158_0x143f2| + 0x4df8
	LDR      r1, [pc, #0x30c]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	ADD      r0, r5, #0
	BL       |sub_08022DF4|
	MOV      r1, #0
	ADD      r0, sp, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r1, #0
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x7c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x2d0]
	ADD      r5, r0, #0
	LDR      r0, [r6, #0xc]
	LDR      r1, [pc, #0x2e8]
	MOV      r2, #0
	ADD      r0, r0, r1
	SUB      sp, #0xc
	STR      r0, [sp, #8]
	LDR      r0, [r0]
	MOV      r1, #0xb
	LSL      r1, r1, #7
	ADD      r1, r5, r1
	STR      r1, [sp, #4]
	STR      r0, [r1]
	CMP      r0, #0
	BEQ      |loc_080231D2|
	MOV      r2, #1
|loc_080231D2|
	MOV      r0, #0
|loc_080231D4|
	LDR      r1, [r6, #0xc]
	ADD      r3, r5, r0
	ADD      r1, r1, r0
	LDRB     r1, [r1, #2]
	ADD      r3, #0xff
	ADD      r3, #0x41
	STRB     r1, [r3, #1]
	CMP      r1, #0
	BEQ      |loc_080231E8|
	MOV      r2, #1
|loc_080231E8|
	ADD      r0, #1
	CMP      r0, #0x53
	BLT      |loc_080231D4|
	LDR      r1, [r6, #0xc]
	ADD      r4, r5, #0
	ADD      r1, #0xe4
	LDR      r3, [r1]
	ADD      r4, #0xff
	ADD      r4, #0x95
	MOV      r0, #0
	CMP      r3, #0
	BLE      |sub_08023220|
|loc_08023200|
	LSL      r2, r0, #2
	ADD      r2, r2, r1
	LDR      r2, [r2, #4]
	ADD      r0, #1
	LSL      r3, r2, #4
	LDR      r2, [r4]
	LSR      r3, r3, #4
	ADD      r7, r2, #1
	LSL      r2, r2, #2
	ADD      r2, r2, r4
	STR      r7, [r4]
	STR      r3, [r2, #4]
	LDR      r2, [r1]
	CMP      r2, r0
	BGT      |loc_08023200|
	B        |sub_08023224|
