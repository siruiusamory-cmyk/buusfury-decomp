	CODE16
|sub_08006D20|
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x24]
	ADD      r3, r2, r1
	MOV      r2, #0
	MOV      r1, #0xc
	BL       |inc_0x046118_0x049114| + 0x98e
	ORR      r5, r0
	LDR      r0, [r6, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08006CFC|
	LDR      r0, [pc, #0x1c]
	MOV      r1, #0xc
	LDR      r0, [r0, #4]
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	SUB      r0, #1
	ORR      r0, r5
	ADD      r1, r0, #0
	MOV      r0, #1
	CMP      r1, #0
	BEQ      |loc_08006D52|
	MOV      r0, #0
|loc_08006D52|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	LSL      r4, r6, #5
	LSR      r7, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08006D74|
	MOV      r0, #4
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08006D74|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
