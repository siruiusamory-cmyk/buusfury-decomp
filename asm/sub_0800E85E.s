	CODE16
|sub_0800E85E|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2d0]
	ADD      r5, r1, #0
	STR      r0, [r4]
	MOV      r0, #0x85
	LSL      r0, r0, #2
	ADD      r0, r4, r0
	BL       |sub_08004102|
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	LDR      r1, [r0, #0x34]
	CMP      r1, #0
	BEQ      |loc_0800E88C|
	ADD      r1, #0xff
	ADD      r1, #0xc1
	LDR      r2, [r1, #0x30]
	CMP      r2, r4
	BNE      |loc_0800E88C|
	LDR      r2, [r0, #0x38]
	STR      r2, [r1, #0x30]
|loc_0800E88C|
	LDR      r1, [r0, #0x3c]
	CMP      r1, #0
	BEQ      |loc_0800E89A|
	ADD      r1, #0xff
	LDR      r2, [r0, #0x38]
	ADD      r1, #0xc1
	STR      r2, [r1, #0x38]
|loc_0800E89A|
	LDR      r1, [r0, #0x38]
	CMP      r1, #0
	BEQ      |loc_0800E8A8|
	ADD      r1, #0xff
	LDR      r2, [r0, #0x3c]
	ADD      r1, #0xc1
	STR      r2, [r1, #0x3c]
|loc_0800E8A8|
	LDR      r0, [r0, #0x30]
	MOV      r1, #0
	CMP      r0, #0
	BEQ      |loc_0800E8BC|
|loc_0800E8B0|
	ADD      r0, #0xff
	ADD      r0, #0xc1
	STR      r1, [r0, #0x34]
	LDR      r0, [r0, #0x38]
	CMP      r0, #0
	BNE      |loc_0800E8B0|
|loc_0800E8BC|
	MOV      r0, #0xff
	ADD      r0, #0x8d
	LDR      r0, [r0, r4]
	CMP      r0, #0
	BEQ      |loc_0800E8D2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800E8D2|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |sub_0800EC34|
	CMP      r5, #0
	BEQ      |loc_0800E8E4|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800E8E4|
	POP      {r3, r4, r5, pc}
