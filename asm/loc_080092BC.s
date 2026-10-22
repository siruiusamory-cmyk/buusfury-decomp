	CODE16
|loc_080092BC|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	MOV      r4, #0
|loc_080092C4|
	LSL      r0, r4, #2
	LDR      r0, [r6, r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, #1
	CMP      r4, #4
	BLT      |loc_080092C4|
	LDR      r0, [r5, #0x18]
	LDR      r1, [r5, #0x1c]
	STR      r0, [r5, #0x38]
	STR      r1, [r5, #0x3c]
	LDR      r0, [r5, #0x40]
	ADD      r0, #1
	STR      r0, [r5, #0x40]
	POP      {r4, r5, r6, pc}
