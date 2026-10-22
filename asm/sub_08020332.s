	CODE16
|sub_08020332|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1f8]
	MOV      r7, #0xff
	LDR      r0, [r0]
	ADD      r7, #0x15
	MOV      r6, #0
	CMP      r0, #0
	LDR      r5, [pc, #0x1f0]
	BEQ      |sub_08020370|
	LDR      r0, [pc, #0x1e8]
	STR      r6, [r0]
	ADD      r0, r7, #0
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08020368|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STMIA    r0!, {r5, r6}
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	STR      r6, [r1, #0x10]
	LDR      r1, [pc, #0x1d4]
	SUB      r0, #8
	STR      r1, [r0]
|loc_08020368|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
