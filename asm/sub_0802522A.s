	CODE16
|sub_0802522A|
|unk_0802522A|
		MOV r1, #0
|loc_0802522C|
|unk_0802522C|
		STR r1, [r0, #0x20]
		LDR r0, [pc, #0xec]
		LDR r1, [pc, #0xe0]
		ADD r0, sp
		BL       |inc_0x03d784_0x041118| + 0x2234
|loc_08025238|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r0, [r3, #0x78]
		LDR r5, [pc, #0xc8]
		LDR r0, [r0, #0x38]
		CMP r0, #0
		BEQ      |loc_08025250|
		ADD r1, r0, #0
		LDR r0, [r5, #0xc]
		BL       |loc_08011944|
|loc_08025250|
		CMP r7, #0
		DCW     0xD01C
		ADD r1, r7, #0
		MOV r0, #0
		BL       |sub_080272EC|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r1, [r3, #0x78]
		ADD r3, #0x80
		STR r0, [r1, #0x38]
		LDR r2, [r3]
		LDRB r1, [r2, #0xe]
		CMP r1, #0
		BEQ      |loc_0802527C|
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #2
		BL       |loc_08046AA4|
|loc_0802527C|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r0, [r3, #0x78]
		LDR r1, [r0, #0x38]
		LDR r0, [r5, #0xc]
	INCBIN  baserom.gba_0x25288_0x2528a.extracted
|sub_0802528A|
|unk_0802528A|
	INCBIN	baserom.gba_0x2528a_0x2528e.extracted
	MOV      r1, #0
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x78]
	STR      r1, [r0, #0x38]
	LDR      r0, [pc, #0x80]
	MOV      r1, #0
	ADD      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	LDR      r2, [r3]
	LDRB     r0, [r2, #0xe]
	CMP      r0, #1
	BNE      |loc_08025330|
	LDR      r2, [r4, #0x1c]
	MOV      r1, #0x68
	ADD      r2, #0x38
	MOV      r0, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	STR      r0, [r4, #0xc]
	LDR      r1, [r5, #0x10]
	STR      r1, [r0, #0xc]
	LDR      r0, [r4, #0xc]
	MOV      r1, #2
	STRB     r1, [r0, #3]
	LDR      r0, [r4, #0xc]
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #0xe
	STR      r1, [r0, #8]
	LDR      r1, [r4, #0xc]
	MOV      r0, #0x10
	STRB     r0, [r1, #1]
	LDR      r0, [r4, #0xc]
	MOV      r1, #0
	LDR      r2, [r0, #0x30]
	LDR      r0, [r0, #0x24]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDRH     r0, [r7, #2]
	LDR      r1, [pc, #0x3c]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	LDR      r0, [r4, #0xc]
	MOV      r1, #0x68
	BL       |inc_0x03d784_0x041118| + 0x5e2
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	LDR      r0, [r3]
	BL       |sub_08025004|
	LDR      r3, [pc, #0x28]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
|sub_08025308|
	DCW      0xa950
	DCW      0x0804,0x19cc,0x0873,0xd380,0x0874,0x9800,0x0600,0xef80
	DCW      0xffff,0x1044,0x0000,0x2350,0x0873,0x0040,0x0600,0xbce8
	DCW      0x0806,0x1084,0x0000
