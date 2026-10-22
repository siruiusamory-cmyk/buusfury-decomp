	CODE16
|sub_08008F10|
	MOV      r0, #0x32
	ADD      r3, sp, #0
	STRH     r0, [r3]
	MOV      r0, #0
	STRH     r0, [r3, #2]
	LDRH     r0, [r5]
	ADD      r0, #0x32
	STRH     r0, [r3]
	LDRH     r0, [r5, #2]
	STRH     r0, [r3, #2]
	LDR      r0, [pc, #0xf0]
	LDR      r0, [r0, #4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_08008F56|
	MOV      r0, #0x55
	LSL      r0, r0, #3
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BEQ      |loc_08008F72|
	ADD      r3, r7, #0
	ADD      r0, r5, #0
	MOV      r2, sp
	LDR      r1, [sp, #0x18]
	BL       |sub_08010A3A|
	LDR      r0, [pc, #0xd8]
	STR      r0, [r5]
	B        |loc_08008F72|
