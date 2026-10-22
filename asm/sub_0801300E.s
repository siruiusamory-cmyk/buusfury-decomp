	CODE16
|sub_0801300E|
	MOV      r0, #0
	MOV      r1, #0xff
	ADD      r1, #0xcd
	STR      r0, [r1, r4]
	ADD      r4, #0xff
	MOV      r0, #0x80
	ADD      r4, #0xb1
	STRB     r0, [r4, #8]
	STRB     r0, [r4, #9]
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	ADD      r7, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	MOV      r6, #0
	LSL      r0, r0, #0x17
	LSR      r0, r0, #0x1f
	CMP      r0, #0
	BEQ      |sub_08013078|
	LDR      r0, [r4, #0x58]
	LDRB     r1, [r0]
	CMP      r1, #7
	BLS      |sub_08013078|
	LDR      r0, [r0, #0x70]
	CMP      r0, #0
	BEQ      |sub_08013078|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08013064|
	LDR      r1, [pc, #0x2d8]
	STR      r1, [r0]
	STR      r6, [r0, #8]
	STR      r6, [r0, #4]
|loc_08013064|
	ADD      r4, r0, #0
	MOV      r1, #7
	ADD      r0, r7, #0
	BL       |Record_SelectIndexed|
	ADD      r1, r4, #0
	ADD      r0, r7, #0
|unk_08013072|
	INCBIN	baserom.gba_0x13072_0x13074.extracted
|loc_08013074|
|unk_08013074|
	INCBIN	baserom.gba_0x13074_0x13076.extracted
	POP      {r3, r4, r5, r6, r7, pc}
