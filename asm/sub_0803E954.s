	CODE16
|sub_0803E954|
	ADD      r1, r0, #0
	ADD      r1, #0x40
	LDRB     r2, [r1, #8]
	LDRB     r3, [r1, #0xb]
	SUB      r2, r2, r3
	LSL      r2, r2, #0x18
	ASR      r2, r2, #0x18
	STRB     r2, [r1, #8]
	CMP      r2, #0
	BGT      |loc_0803E970|
	MOV      r2, #0
	STRB     r2, [r1, #8]
	LDR      r2, [pc, #0xf0]
	STR      r2, [r0, #0x54]
|loc_0803E970|
	LDRB     r1, [r1, #8]
	MOV      r2, #0x10
	STRB     r1, [r0, #0x12]
	LDRB     r1, [r0, #0x10]
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	B        |Math_ScaleByTable1|
	ADD      r1, r0, #0
	ADD      r1, #0x40
	LDRB     r2, [r1, #8]
	LDRB     r3, [r1, #0xb]
	ADD      r2, r2, r3
	LSL      r2, r2, #0x18
	ASR      r2, r2, #0x18
	STRB     r2, [r1, #8]
	CMP      r2, #0x40
	BLT      |loc_0803E99A|
	MOV      r2, #0x40
	STRB     r2, [r1, #8]
	LDR      r2, [pc, #0xc8]
	STR      r2, [r0, #0x54]
|loc_0803E99A|
	LDRB     r1, [r1, #8]
	MOV      r2, #0x10
	STRB     r1, [r0, #0x12]
	LDRB     r1, [r0, #0x10]
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	B        |Math_ScaleByTable1|
|sub_0803E9A8|
|unk_0803E9A8|
	INCBIN	baserom.gba_0x3e9a8_0x3ea24.extracted
