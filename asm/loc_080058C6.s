	CODE16
|loc_080058C6|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	ADD      r6, r0, #0
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0xbf
	LSL      r0, r0, #2
	ADD      r7, r6, #0
	ADD      r7, #0xff
	ADD      r5, r6, r0
	SUB      r0, #0x3c
	ADD      r7, #1
	LDR      r4, [r7, #0xc]
	ADD      r0, r6, r0
	LDR      r6, [r0, #0x38]
	MOV      r0, #0xff
	ADD      r0, #0x25
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08005914|
	LDR      r1, [pc, #0xc0]
	MOV      r2, #0
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r2, [r1, #0xc]
	STR      r2, [r1, #8]
	STR      r2, [r1, #0x10]
	LDR      r2, [pc, #0xb0]
	STR      r2, [r0]
	STR      r4, [r1, #0x14]
	LDMIA    r5!, {r2, r3}
	ADD      r1, #0x18
	STMIA    r1!, {r2, r3, r6}
|loc_08005914|
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	LDR      r0, [pc, #0xa0]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	MOV      r2, #0
	STRH     r2, [r0]
	LDR      r0, [r7, #0xc]
	LDR      r1, [pc, #0x84]
	STR      r0, [r1]
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0xf2
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	CMP      r2, #0
	BEQ      |loc_0800597C|
	MOV      r4, #0
	CMP      r2, #1
	BNE      |loc_08005984|
	LSL      r2, r2, #9
	MOV      r1, #0
	LDR      r0, [pc, #0x64]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r4, [r0]
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, pc}
|loc_0800597C|
	BL       |loc_080058C6|
	MOV      r0, #1
	POP      {r4, pc}
|loc_08005984|
	ADD      r0, #0xff
	ADD      r0, #1
	CMP      r2, #2
	BEQ      |sub_080059A0|
	CMP      r2, #3
	BNE      |loc_0800599C|
	LDR      r1, [r0, #0xc]
	CMP      r1, #2
	BGE      |loc_0800599A|
	ADD      r1, #1
	STR      r1, [r0, #0xc]
|loc_0800599A|
	STR      r4, [r0, #0x10]
|loc_0800599C|
	ADD      r0, r4, #0
	POP      {r4, pc}
