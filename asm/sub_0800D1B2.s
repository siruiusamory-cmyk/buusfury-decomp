	CODE16
|sub_0800D1B2|
	LSL      r0, r0, #0
|unk_0800D1B4|
	INCBIN	baserom.gba_0xd1b4_0xd1b6.extracted
	LSR      r4, r0, #0x20
	BNE      |loc_0800D184|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0xbc]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0x16]
	LDR      r0, [pc, #0xb8]
	CMP      r1, r0
	BEQ      |loc_0800D1D6|
	LDR      r0, [pc, #0xb8]
	LDR      r0, [r0]
	BL       |loc_0801142A|
|loc_0800D1D6|
	LDR      r0, [r4, #0xc]
	CMP      r0, #0
	BEQ      |loc_0800D1E8|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800D1E8|
	LDR      r0, [pc, #0xa0]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0800D1F6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800D1F6|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDRH     r1, [r0, #0x16]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x88]
	LDR      r0, [r0]
	BL       |loc_0801142A|
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #0x16]
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r0, #0x16]
	LDR      r1, [pc, #0x6c]
	CMP      r0, r1
	BNE      |loc_0800D230|
	LDR      r0, [r4, #0x34]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x64]
	LDR      r0, [r0]
	BL       |loc_0801124C|
	STRH     r0, [r4, #0x16]
	ADD      r0, r4, #0
	BL       |sub_0800D026|
|loc_0800D230|
	POP      {r4, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r1, #0xb
	BNE      |loc_0800D248|
	ADD      r0, r4, #0
	BL       |sub_0800D026|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_0800D248|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	ADD      r0, #0xc
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	CMP      r0, #0
	BEQ      |loc_0800D25A|
	SUB      r0, #1
|loc_0800D258|
	POP      {r4, r5, r6, pc}
|loc_0800D25A|
	MOV      r0, #0
	CMP      r5, #4
	BNE      |loc_0800D272|
	LDRH     r2, [r4, #0x14]
	ASR      r1, r6, #1
	CMP      r1, r2
	BNE      |loc_0800D258|
	LSL      r0, r6, #0x1f
	LSR      r0, r0, #0x1f
	STR      r0, [r4, #0x1c]
	MOV      r0, #1
|loc_0800D270|
	POP      {r4, r5, r6, pc}
|loc_0800D272|
	CMP      r5, #8
	BNE      |loc_0800D270|
	LDRH     r1, [r4, #0x14]
	CMP      r1, r6
	BNE      |loc_0800D270|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800D280|
	DCW      0xd1e4
	DCW      0x0804,0xffff,0x0000,0x2580,0x0807,0xe454
|loc_0800D28E|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_0800D2AA|
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800D2AA|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800D2AA|
	BL       |loc_0800776C|
	ADD      r3, r0, #0
	LDR      r0, [pc, #0x264]
	STR      r0, [r4]
	LDR      r0, [r5]
	LDR      r1, [r5, #4]
	ADD      r5, #8
	LDMIA    r5!, {r2, r5}
	SUB      r0, #0xf
	STRH     r0, [r4, #4]
	SUB      r1, #7
	STRH     r1, [r4, #6]
	STRH     r2, [r4, #8]
	LDR      r0, [pc, #0x254]
	STRH     r5, [r4, #0xa]
	STR      r0, [r4]
	STR      r3, [r4, #0xc]
	STR      r6, [r4, #0x10]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	LDR      r3, [r2, #0x28]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x238]
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x10]
	BL       |loc_0801268A|
	POP      {r4, pc}
	CMP      r0, #0
	BLT      |loc_0800D300|
	MOV      r3, #0x34
	LDR      r1, [pc, #0x22c]
	MUL      r0, r3
	ADD      r0, r0, r1
	ADD      r0, #0xc
	BX       lr
