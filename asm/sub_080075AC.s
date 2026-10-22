	CODE16
|sub_080075AC|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r0, r1, #0
	ADD      r5, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	SUB      sp, #0xc
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	LDRB     r1, [r6, #0x11]
	AND      r0, r1
	BEQ      |loc_08007634|
	LDR      r1, [r5]
	LDR      r4, [r6, #0x14]
	LDR      r2, [r1, #0x34]
	ADD      r0, r5, #0
	ADD      r2, r2, r1
	MOV      r1, #2
	BL       |inc_0x046118_0x049114| + 0x98c
	STR      r0, [sp, #8]
	MOV      r0, #0x11
	LSL      r0, r0, #5
	ADD      r0, r5, r0
	LDRH     r7, [r0, #0x10]
	LDRB     r0, [r6, #0x10]
	ADD      r1, r5, #0
	STRB     r0, [r5, #0x10]
	MOV      r0, #0
	BL       |loc_08006D98|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDRB     r1, [r4, #0x13]
	MOV      r2, #1
	STR      r2, [sp, #4]
	ADD      r3, r4, #0
	LDR      r6, [pc, #0xac]
	STR      r1, [sp]
	ADD      r3, #0x14
	SUB      r6, #8
	LDRB     r2, [r4, #0x12]
	LDRB     r1, [r4, #0x11]
	LDR      r0, [r6]
	BL       |loc_08008D44|
	ADD      r5, r0, #0
	LDR      r0, [r6, #4]
	ADD      r0, #0x80
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |sub_08007638|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08007630|
	LDR      r1, [pc, #0x88]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #4
	STR      r1, [r0, #8]
|loc_08007630|
	BL       |inc_0x03d784_0x041118| + 0x11c
|loc_08007634|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
