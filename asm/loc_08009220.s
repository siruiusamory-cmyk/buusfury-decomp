	CODE16
|loc_08009220|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	MOV      r4, #0
|loc_08009226|
	LSL      r6, r4, #2
	LDR      r0, [r5, r6]
	CMP      r0, #0
	BEQ      |loc_0800923A|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800923A|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |sub_08007A40|
	ADD      r4, #1
	CMP      r4, #4
	STR      r0, [r5, r6]
	BLT      |loc_08009226|
	POP      {r4, r5, r6, pc}
