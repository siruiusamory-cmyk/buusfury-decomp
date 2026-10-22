	CODE16
|sub_0803A052|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A082|
	LDR      r1, [pc, #0x20]
	MOV      r3, #4
	STR      r1, [r0]
	LDRSH    r1, [r4, r3]
	MOV      r3, #6
	LDRSH    r2, [r4, r3]
	STR      r1, [r0, #4]
	MOV      r3, #8
	STR      r2, [r0, #8]
	LDRSH    r1, [r4, r3]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0x81
	STR      r1, [r0, #0xc]
	ADD      r1, r2, #0
	MUL      r1, r2
	STR      r1, [r0, #0x10]
|loc_0803A082|
	POP      {r4, pc}
|sub_0803A084|
|unk_0803A084|
	INCBIN	baserom.gba_0x3a084_0x3a086.extracted
