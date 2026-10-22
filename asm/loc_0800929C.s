	CODE16
|loc_0800929C|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	ADD      r6, r1, #0
	MOV      r4, #0
|loc_080092A4|
	LSL      r0, r4, #2
	LDR      r0, [r5, r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r6, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, #1
	CMP      r4, #4
	BLT      |loc_080092A4|
	POP      {r4, r5, r6, pc}
