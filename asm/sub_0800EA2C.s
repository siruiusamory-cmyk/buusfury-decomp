	CODE16
|sub_0800EA2C|
	LDR      r2, [sp, #0x28]
	LDR      r3, [pc, #0x110]
	LDRH     r0, [r2, #0x10]
	LDR      r2, [sp, #0x2c]
	MUL      r0, r5
	MUL      r0, r3
	ASR      r5, r0, #0x10
	LDRB     r0, [r2, #8]
	STR      r0, [sp, #0x20]
	LDR      r0, [sp, #0x30]
	LDRH     r0, [r0, #0x14]
	B        |loc_0800EA54|
|loc_0800EA44|
	LDRH     r7, [r2, #0x12]
	LDR      r2, [sp, #0x2c]
	MOV      r1, #0
	LDRB     r0, [r2, #9]
	STR      r0, [sp, #0x20]
	LDR      r0, [sp, #0x30]
	LDRH     r0, [r0, #0x16]
	STR      r1, [r4, #0x10]
|loc_0800EA54|
	CMP      r0, #0xc8
	BLT      |loc_0800EA68|
	ASR      r1, r0, #0x1f
	LSR      r1, r1, #0x1e
	ADD      r0, r1, r0
	ASR      r0, r0, #2
	ADD      r0, #0x96
	CMP      r0, #0xdc
	BLE      |loc_0800EA68|
	MOV      r0, #0xdc
|loc_0800EA68|
	MOV      r1, #0xdd
	SUB      r0, r1, r0
	ADD      r1, r7, #0
	ADD      r2, r7, #0
	ADD      r2, #0x64
	MUL      r1, r7
	MUL      r0, r5
	MOV      r3, #0xff
	ADD      r3, #0x2a
	MUL      r1, r2
	ASR      r1, r1, #0xd
	ADD      r5, r1, r7
	LDR      r1, [r4, #4]
	MUL      r0, r3
	ASR      r0, r0, #0x10
	MUL      r1, r0
	MOV      r0, #1
	LSL      r0, r0, #0xa
	ADD      r0, r1, r0
	SUB      r0, #1
	ASR      r7, r0, #0xa
	MOV      r0, #0x1a
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #0xff
	ADD      r0, #1
	MUL      r0, r7
	LSR      r0, r0, #8
	MUL      r0, r5
	ADD      r1, r0, #0
	STR      r1, [r4, #0x14]
	LDR      r0, [sp, #0x20]
	BL       |inc_0x046118_0x049114| + 0xa58
	MOV      r2, #0x7f
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #7
	BL       |inc_0x046118_0x049114| + 0xb10
	ADD      r7, r6, #0
	ADD      r7, #0xff
	ADD      r7, #0xc1
	STR      r0, [r4, #0x18]
	LDR      r1, [r7, #8]
	ADD      r5, r4, #0
	ADD      r5, #0x18
	CMP      r1, #0
	BEQ      |loc_0800EAEC|
	LDRB     r1, [r4]
	MOV      r2, #1
	EOR      r1, r2
	LDRB     r2, [r6, #0x10]
	CMP      r1, r2
	BNE      |loc_0800EAEC|
	LDR      r1, [r5]
	CMP      r1, #0
	BEQ      |loc_0800EAEC|
	ADD      r1, r0, #0
	LDR      r0, [r7]
	BL       |inc_0x046118_0x049114| + 0xa58
	MOV      r2, #0x10
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [r4, #0x18]
|loc_0800EAEC|
	LDR      r0, [r4, #8]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |loc_0800EB30|
	ADD      r0, r5, #0
	LDR      r0, [r0]
	MOV      r5, #0
	CMP      r0, #0
	BEQ      |loc_0800EB30|
	LDR      r1, [r4, #0x18]
	LDR      r0, [r7, #4]
	BL       |inc_0x046118_0x049114| + 0xa58
	MOV      r2, #8
	BL       |inc_0x046118_0x049114| + 0xb10
	CMP      r0, #0
	BEQ      |loc_0800EB30|
	STR      r0, [sp, #0x1c]
	STR      r0, [sp, #0x18]
	STR      r5, [sp, #0x14]
	STR      r6, [sp, #0x10]
	LDRB     r0, [r4]
	MOV      r2, #1
	ADD      r3, sp, #0
	EOR      r0, r2
	STRB     r0, [r3, #4]
	LDR      r0, [sp, #0x24]
	ADD      r1, sp, #4
	LDR      r2, [r0]
	LDR      r3, [r2, #0x5c]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800EB30|
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_0800EB34|
|unk_0800EB34|
	INCBIN	baserom.gba_0xeb34_0xeb36.extracted
