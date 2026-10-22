	CODE16
|loc_0800927E|
	PUSH     {r4, r5, r6, lr}
	LSL      r5, r1, #2
	ADD      r4, r0, #0
	LDR      r0, [r0, r5]
	ADD      r6, r2, #0
	CMP      r0, #0
	BEQ      |loc_08009298|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08009298|
	STR      r6, [r4, r5]
	POP      {r4, r5, r6, pc}
