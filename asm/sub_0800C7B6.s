	CODE16
|sub_0800C7B6|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x8c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x2c]
	CMP      r0, #0
	BEQ      |loc_0800C7D2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800C7D2|
	LDR      r0, [pc, #0x80]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0800C7E0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800C7E0|
	POP      {r3, r4, r5, pc}
