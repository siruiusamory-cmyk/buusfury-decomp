	CODE16
|sub_08024D94|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x180]
	SUB      sp, #8
	LDR      r0, [r0, #0xc]
	MOV      r7, #2
	STR      r0, [r1, #0xc]
	STRB     r7, [r1, #3]
	ADD      r4, r1, #0
	MOV      r1, #1
	LDR      r0, [pc, #0x174]
	STRB     r1, [r4, #2]
	STR      r0, [r4, #0x20]
	MOV      r0, #0x38
	STR      r0, [r4, #4]
	MOV      r0, #0x90
	STR      r0, [r4, #8]
	MOV      r0, #8
	STRB     r0, [r4, #1]
	STRB     r1, [r4]
	CMP      r5, #0
	LDR      r6, [pc, #0x164]
	BEQ      |loc_08024DCE|
	LDRH     r0, [r5]
	LSL      r0, r0, #2
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
|loc_08024DCE|
	MOV      r7, #2
	STRB     r7, [r4, #3]
	MOV      r0, #0
	STRB     r0, [r4]
	MOV      r0, #0x16
	STR      r0, [r4, #8]
	MOV      r0, #0x5f
	MOV      r7, #0x70
	LDR      r6, [pc, #0x144]
	STR      r7, [r4, #4]
	LSL      r0, r0, #3
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r0, #0x20
	STR      r0, [r4, #8]
	MOV      r0, #0xbf
	LSL      r0, r0, #2
	STR      r7, [r4, #4]
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r0, #0x2a
	STR      r0, [r4, #8]
	MOV      r0, #3
	LSL      r0, r0, #8
	STR      r7, [r4, #4]
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r0, #0x34
	STR      r0, [r4, #8]
	MOV      r0, #0xc1
	LSL      r0, r0, #2
	STR      r7, [r4, #4]
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r7, #2
	STRB     r7, [r4]
	STRB     r7, [r4, #3]
	SUB      r6, r7, #3
	ADD      r7, r6, #0
	CMP      r5, #0
	STR      r6, [sp, #4]
	LDR      r2, [sp, #0x10]
	BEQ      |sub_08024E88|
	LDR      r0, [r5, #0xc]
	CMP      r0, r6
	BEQ      |sub_08024E88|
	CMP      r0, #0
	BGE      |sub_08024E70|
	ADD      r0, #2
|unk_08024E40|
	INCBIN	baserom.gba_0x24e40_0x24e42.extracted
	MOV      r3, #0x68
	LDR      r0, [pc, #0xd4]
	MUL      r1, r3
	LDR      r0, [r0, #8]
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	CMP      r2, r6
	BNE      |loc_08024E5E|
	ADD      r1, r0, #0
	ADD      r1, #0x16
	MOV      r3, #0
	LDRSH    r2, [r1, r3]
|loc_08024E5E|
	ADD      r1, r0, #0
	ADD      r1, #0x4c
	LDRH     r6, [r1]
	STR      r6, [sp, #4]
	ADD      r1, #2
	LDRH     r6, [r1]
	ADD      r0, #0x50
	LDRH     r7, [r0]
	B        |sub_08024E88|
