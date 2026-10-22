	CODE16
|sub_0801782C|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #1
	LSL      r0, r0, #0xa
	ADD      r4, r5, r0
	LDR      r0, [r4, #4]
	ADD      r0, #1
	LSL      r1, r0, #8
	STR      r0, [r4, #4]
	LDR      r0, [r4, #8]
	BL       |inc_0x046118_0x049114| + 0xd40
	ADD      r1, r0, #0
	ADD      r0, r5, #0
	BL       |loc_0801774C|
	ADD      r1, r4, #4
	LDMIA    r1!, {r0, r1}
	CMP      r0, r1
	BLT      |sub_08017858|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
