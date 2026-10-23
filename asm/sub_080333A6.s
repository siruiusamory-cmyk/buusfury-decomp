	CODE16
|sub_080333A6|
	LSR      r4, r0, #0x20
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [pc, #0x204]
	LSL      r2, r2, #2
	ADD      r3, r2, r3
	LSL      r0, r0, #2
	LDR      r3, [r3, r0]
	STR      r3, [r1, #8]
	LDR      r3, [pc, #0x1f8]
	ADD      r3, #0x18
	ADD      r2, r2, r3
	LDR      r0, [r2, r0]
	STR      r0, [r1, #0x10]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	SUB      sp, #0x3c
	ADD      r5, r1, #0
	ADD      r6, r2, #0
	ADD      r0, sp, #0x28
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	MOV      r0, #0xff
	ADD      r0, #0xa1
	LDR      r0, [r0, r5]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x24]
	MOV      r0, #0xff
	ADD      r0, #0xa5
	LDR      r0, [r0, r5]
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x26]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x74]
	ADD      r3, r2, r1
	ADD      r2, r6, #0
	LDR      r1, [r4, #0x10]
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r6, [pc, #0x1b8]
	ADD      r1, r5, #0
	SUB      r6, #0x24
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_08033442|
	LDR      r0, [sp, #0x28]
	LDR      r2, [sp, #0x30]
	LDR      r3, [sp, #0x34]
	ADD      r2, r0, r2
	STR      r2, [sp, #0x14]
	ASR      r2, r2, #1
	LDR      r0, [sp, #0x2c]
	STR      r2, [sp, #0x14]
	ADD      r0, r0, r3
	STR      r0, [sp, #0x18]
	ASR      r0, r0, #1
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x38
	STR      r0, [sp, #0x18]
	STR      r0, [sp, #0x20]
	MOV      r0, #0
	ADD      r1, sp, #0x1c
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08033442|
	LDR      r1, [pc, #0x170]
	MOV      r2, #0x20
	ADD      r5, sp, #4
	SUB      r1, #0x20
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0x24]
	STRH     r0, [r3, #0x10]
	LDRH     r0, [r3, #0x26]
	STRH     r0, [r3, #0x12]
	LDR      r7, [r4, #0xc]
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x14c]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LSL      r2, r7, #2
	LDR      r1, [r1, r2]
	MOV      r7, #0
	STR      r1, [sp, #0xc]
	LDR      r1, [pc, #0x13c]
	MVN      r7, r7
	ADD      r1, #0x18
	ADD      r0, r0, r1
	LDR      r0, [r0, r2]
	LDR      r1, [pc, #0x138]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r7, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0x114]
	MOV      r2, #0x20
	SUB      r1, #0x20
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0x24]
	ADD      r0, #0x18
	STRH     r0, [r3, #0x10]
	LDRH     r0, [r3, #0x26]
	STRH     r0, [r3, #0x12]
	LDR      r2, [r4, #0xc]
	MOV      r0, #2
	STR      r2, [sp]
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0xec]
	LDR      r2, [sp]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LSL      r2, r2, #2
	LDR      r1, [r1, r2]
	STR      r1, [sp, #0xc]
	LDR      r1, [pc, #0xe0]
	ADD      r1, #0x18
	ADD      r0, r0, r1
	LDR      r0, [r0, r2]
	LDR      r1, [pc, #0xdc]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r7, #0
	ADD      r1, r5, #0
|loc_080334EC|
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0xb8]
	MOV      r2, #0x20
	SUB      r1, #0x20
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0x24]
	ADD      r0, #0x18
	STRH     r0, [r3, #0x10]
	LDRH     r0, [r3, #0x26]
	ADD      r0, #0x18
	STR      r0, [sp, #0x38]
	STRH     r0, [r3, #0x12]
	LDR      r2, [r4, #0xc]
	MOV      r0, #2
	STR      r2, [sp]
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x8c]
	LDR      r2, [sp]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LSL      r2, r2, #2
	LDR      r1, [r1, r2]
	STR      r1, [sp, #0xc]
	LDR      r1, [pc, #0x80]
	ADD      r1, #0x18
	ADD      r0, r0, r1
	LDR      r0, [r0, r2]
	LDR      r1, [pc, #0x7c]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r7, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0x58]
	MOV      r2, #0x20
	SUB      r1, #0x20
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0x24]
	STRH     r0, [r3, #0x10]
	LDR      r0, [sp, #0x38]
	STRH     r0, [r3, #0x12]
	LDR      r4, [r4, #0xc]
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x34]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LSL      r2, r4, #2
	LDR      r1, [r1, r2]
	STR      r1, [sp, #0xc]
	LDR      r1, [pc, #0x28]
	ADD      r1, #0x18
	ADD      r0, r0, r1
	LDR      r0, [r0, r2]
	LDR      r1, [pc, #0x24]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r7, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_080335B4|
|unk_080335B4|
	INCBIN	baserom.gba_0x335b4_0x335b6.extracted
|sub_080335B6|
	DCW      0x0875
	DCW      0x1274
	DCW      0x0871
