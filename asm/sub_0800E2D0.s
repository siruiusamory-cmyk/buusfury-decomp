	CODE16
|sub_0800E2D0|
	LDRH     r3, [r1]
	ADD      r2, r3, r2
	LSL      r2, r2, #0x10
	ASR      r2, r2, #0x10
|loc_0800E2D8|
	STRH     r2, [r1]
	MOV      r3, #0
	LDRSH    r5, [r1, r3]
	CMP      r5, r2
	BNE      |loc_0800E2D8|
|loc_0800E2E2|
	ADD      r0, #1
	CMP      r0, #9
	BLT      |loc_0800E25E|
	LDR      r0, [r4, #0xc]
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STR      r0, [r4, #0xc]
|loc_0800E2F0|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	BL       |loc_08013C66|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_0800E074|
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDRH     r1, [r0, #0x10]
	ADD      r1, #5
	STRH     r1, [r0, #0x10]
	LDRH     r1, [r0, #0x12]
	ADD      r1, #5
	STRH     r1, [r0, #0x12]
	LDRH     r1, [r0, #0x14]
	ADD      r1, #5
	STRH     r1, [r0, #0x14]
	LDRH     r1, [r0, #0x16]
	ADD      r1, #5
	STRH     r1, [r0, #0x16]
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r1, [r0, #0x38]
	ADD      r1, #0x80
	STR      r1, [r0, #0x38]
	LDR      r1, [r0, #0x3c]
	ADD      r1, #0x80
	STR      r1, [r0, #0x3c]
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	BL       |loc_08013C66|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_0800E074|
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDRH     r1, [r0, #0x10]
	ADD      r1, #5
	STRH     r1, [r0, #0x10]
	LDRH     r1, [r0, #0x12]
	ADD      r1, #5
	STRH     r1, [r0, #0x12]
	LDRH     r1, [r0, #0x14]
	ADD      r1, #5
	STRH     r1, [r0, #0x14]
	LDRH     r1, [r0, #0x16]
	ADD      r1, #5
	STRH     r1, [r0, #0x16]
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r1, [r0, #0x38]
	ADD      r1, #0x80
	STR      r1, [r0, #0x38]
	LDR      r1, [r0, #0x3c]
	ADD      r1, #0x80
	STR      r1, [r0, #0x3c]
	POP      {r3, r4, r5, pc}
|loc_0800E396|
	DCW      0x0000
	DCW      0x2b44,0x0300,0xd028,0x0877,0x82ec,0x086b,0x25e0,0x0807
	DCW      0x07ae,0x0000,0x0ccd,0x0000,0xe70e
