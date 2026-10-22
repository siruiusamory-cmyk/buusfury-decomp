	CODE16
|sub_0801795C|
|unk_0801795C|
		LDR r0, [r0, #0x14]
		LDR r1, [r0]
		LDR r2, [r1]
		ADD r1, r2, r1
	INCBIN  baserom.gba_0x17964_0x17966.extracted
|sub_08017966|
|unk_08017966|
	INCBIN	baserom.gba_0x17966_0x1796a.extracted
	PUSH     {r4, lr}
	LDR      r2, [r1]
	SUB      sp, #0x10
	ADD      r4, r2, #0
	ADD      r2, #8
	STR      r2, [r1]
	LDR      r1, [pc, #0x68]
	MOV      r2, #3
	STR      r1, [r4]
	LDR      r1, [r4, #4]
	LSL      r2, r2, #0xa
	BIC      r1, r2
	STR      r1, [r4, #4]
	LDRH     r2, [r0, #0xc]
	LSR      r1, r1, #0xa
	LSL      r1, r1, #0xa
	LSL      r2, r2, #0x16
	LSR      r2, r2, #0x16
	ORR      r1, r2
	STR      r1, [r4, #4]
	LDR      r1, [r0, #0x14]
	LDR      r0, [r1]
	LDR      r2, [r0, #4]
	ADD      r2, r2, r0
	MOV      r0, sp
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, sp, #0
	LDMIA    r1!, {r0, r1}
	STR      r0, [sp, #8]
	STR      r1, [sp, #0xc]
	LDR      r1, [r4]
	SUB      r0, #0x10
	LDR      r2, [pc, #0x34]
	LSL      r0, r0, #0x17
	LSR      r0, r0, #7
	AND      r1, r2
	ORR      r0, r1
	LDR      r1, [sp, #0xc]
	LSR      r0, r0, #8
	ADD      r1, #0xf4
	LSL      r1, r1, #0x18
	LSL      r0, r0, #8
	LSR      r1, r1, #0x18
	ORR      r0, r1
	STR      r0, [r4]
	ADD      sp, #0x10
	MOV      r0, #0
	POP      {r4, pc}
|loc_080179CC|
	DCW      0x9680
	DCW      0x0804,0x9ec4,0x086f,0xc974,0x0804,0x7e8c,0x086b,0x0000
	DCW      0x0601,0x2000,0x4000,0xffff
|sub_080179E6|
|unk_080179E6|
	INCBIN	baserom.gba_0x179e6_0x179ea.extracted
	ADD      r4, r0, #0
	BNE      |loc_080179FC|
	MOV      r0, #0x3c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080179FC|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_080179FC|
	LDR      r0, [pc, #0x1dc]
	MOV      r2, #0xa0
	STR      r0, [r4]
	ADD      r0, r4, #0
	MOV      r1, #0xf0
	ADD      r0, #8
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r0, #0
	STR      r0, [r4, #4]
	ADD      r0, r4, #0
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	MOV      r2, #3
	LSL      r2, r2, #0xf
	ADD      r5, r0, #0
	MOV      r1, #0
	LSL      r0, r2, #0xa
	SUB      sp, #0x14
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #2
	LDR      r0, [pc, #0x1b0]
	BL       |inc_0x049120_0x055620| + 0x48
	MOV      r0, #5
	STR      r0, [sp, #8]
	MOV      r0, #0x1e
	MOV      r4, #0
	MOV      r6, #0x10
	STR      r0, [sp, #0xc]
	ADD      r0, sp, #4
	STR      r6, [sp, #0x10]
	MOV      r2, #2
	STR      r4, [sp, #4]
	LDR      r1, [pc, #0x198]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r0, [pc, #0x194]
	LDR      r1, [r5, #0x2c]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r0, #0x28
	STR      r0, [sp, #8]
	MOV      r0, #0xf0
	STR      r0, [sp, #0xc]
	MOV      r0, #0x80
	STR      r0, [sp, #0x10]
	ADD      r0, r5, #0
	ADD      r0, #8
	ADD      r7, r0, #0
	STR      r4, [sp, #4]
	ADD      r2, sp, #4
	LDR      r1, [pc, #0x17c]
	BL       |inc_0x049120_0x055620| + 0x3c
	LSL      r2, r6, #7
	LDR      r1, [pc, #0x178]
	LDR      r0, [pc, #0x178]
	BL       |inc_0x049120_0x055620| + 0x48
	MOV      r0, #5
	STR      r0, [sp, #8]
	MOV      r0, #0x1e
	STR      r0, [sp, #0xc]
	ADD      r0, sp, #4
	STR      r4, [sp, #4]
	STR      r6, [sp, #0x10]
	LDR      r2, [pc, #0x160]
	LDR      r1, [pc, #0x164]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r0, [pc, #0x160]
	LDR      r1, [r5, #0x2c]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r0, #0x28
	STR      r0, [sp, #8]
	MOV      r0, #0xf0
	STR      r0, [sp, #0xc]
	MOV      r0, #0x80
	STR      r0, [sp, #0x10]
	ADD      r0, r7, #0
	STR      r4, [sp, #4]
	ADD      r2, sp, #4
	LDR      r1, [pc, #0x14c]
	BL       |inc_0x049120_0x055620| + 0x3c
	LDR      r0, [pc, #0x148]
	LSL      r1, r6, #0x16
	STRH     r0, [r1, #0xe]
	LDR      r0, [pc, #0x148]
	STRH     r0, [r1, #0xc]
	STRH     r4, [r1, #0x18]
	STRH     r4, [r1, #0x1a]
	STRH     r4, [r1, #0x1c]
	MOV      r0, #3
	LSL      r0, r0, #0xa
	STRH     r4, [r1, #0x1e]
	STRH     r0, [r1]
	LDR      r0, [pc, #0x138]
	ADD      r1, #0x40
	STRH     r0, [r1, #0x10]
	LDR      r0, [pc, #0x138]
	LDR      r1, [pc, #0x138]
	STRB     r6, [r0]
	SUB      r0, #1
	STRB     r4, [r0]
	LSR      r2, r0, #0x11
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	SUB      sp, #0x10
	ADD      r0, #1
	STR      r0, [r4, #4]
	CMP      r0, #0xa0
	BGT      |Blend_WriteAlpha2|
	MOV      r0, #0
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
