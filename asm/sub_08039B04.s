	CODE16
|sub_08039B04|
	CMP      r0, #0x10
	BNE      |sub_08039B6C|
	LDR      r0, [r4, #8]
	MOV      r5, #0
	CMP      r0, #0
	BLE      |loc_08039B5A|
|loc_08039B10|
	LDR      r1, [pc, #0xb8]
	MOV      r2, #0x20
	ADD      r7, sp, #4
	SUB      r1, #0x20
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LSL      r0, r5, #3
	ADD      r2, sp, #0x24
	LDR      r1, [r2, r0]
	ADD      r3, sp, #0
	STRH     r1, [r3, #0x10]
	ADD      r0, r0, r2
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0xa4]
	STRH     r0, [r3, #0x12]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r7, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x80]
	SUB      r0, #0x24
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r0, [r4, #8]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_08039B10|
|loc_08039B5A|
	LDR      r1, [r6]
	ADD      r0, r6, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
