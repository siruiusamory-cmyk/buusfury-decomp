	CODE16
|loc_080119BC|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [r0, #4]
	ADD      r5, r2, #0
	MOV      r2, #0
	ADD      r4, r0, #4
	CMP      r6, #0
	BLE      |loc_080119DA|
|loc_080119CA|
	LSL      r3, r2, #2
	ADD      r3, r3, r4
	LDR      r3, [r3, #4]
	CMP      r3, r1
	BEQ      |loc_080119DE|
	ADD      r2, #1
	CMP      r6, r2
	BGT      |loc_080119CA|
|loc_080119DA|
	MOV      r2, #0
	MVN      r2, r2
|loc_080119DE|
	ADD      r3, r2, #1
	BEQ      |sub_080119EA|
	LSL      r0, r2, #2
	ADD      r0, r0, r4
	STR      r5, [r0, #4]
	POP      {r3, r4, r5, r6, r7, pc}
