	CODE16
|sub_0800F4E6|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_08011818|
	LDR      r0, [r4, #0x58]
	LDR      r0, [r0, #0x50]
	CMP      r0, #0
	BEQ      |loc_0800F500|
	MOV      r2, #0x80
	LDR      r1, [pc, #0x88]
	LDR      r0, [pc, #0x8c]
	BL       |inc_0x049120_0x055620| + 0x5370
|loc_0800F500|
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_0800F510|
	LDRH     r2, [r0, #2]
	LDR      r1, [r0, #4]
	LDR      r0, [r0, #8]
	BL       |inc_0x049120_0x055620| + 0x5370
|loc_0800F510|
	MOV      r0, #0
	STR      r0, [r4, #0x30]
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x58]
	LDR      r0, [r0, #0x50]
	CMP      r0, #0
	BEQ      |loc_0800F528|
	LDR      r0, [pc, #0x64]
	BL       |inc_0x049120_0x055620| + 0x6d00
|loc_0800F528|
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_0800F534|
	LDR      r0, [r0, #8]
	BL       |inc_0x049120_0x055620| + 0x6d00
|loc_0800F534|
	ADD      r0, r4, #0
	BL       |sub_08011568|
	POP      {r4, pc}
	LDRB     r1, [r0, #0x11]
	STR      r1, [r0, #0x1c]
	LDRH     r1, [r0, #0x12]
	STR      r1, [r0, #0x20]
	LDR      r1, [r0, #0x14]
	STR      r1, [r0, #0x24]
	LDR      r1, [r0, #0x50]
	STR      r1, [r0, #0x28]
	LDR      r1, [r0, #0x4c]
	STR      r1, [r0, #0x2c]
	LDR      r1, [pc, #0x34]
	SUB      r1, #4
	STR      r1, [r0, #0x14]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x24]
	STR      r0, [r4, #0x14]
	LDR      r0, [r4, #0x1c]
	STRB     r0, [r4, #0x11]
	LDR      r0, [r4, #0x20]
	STRH     r0, [r4, #0x12]
	LDR      r0, [r4, #0x28]
	STR      r0, [r4, #0x50]
	LDR      r0, [r4, #0x2c]
	STR      r0, [r4, #0x4c]
	MOV      r0, #0
	STR      r0, [r4, #0x24]
	POP      {r4, pc}
|sub_0800F584|
|unk_0800F584|
	INCBIN	baserom.gba_0xf584_0xf586.extracted
