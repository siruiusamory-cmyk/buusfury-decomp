	CODE16
|sub_080531A4|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r7, r1, #0
	CMP      r0, r1
	BCS      |loc_080531FC|
	SUB      r0, r7, r5
	ASR      r0, r0, #3
	LSL      r0, r0, #2
	ADD      r4, r0, r5
	CMP      r5, r4
	BEQ      |loc_080531E8|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_08052EE0|
	CMP      r0, #0
	BEQ      |loc_080531CE|
	LDR      r1, [r4]
	LDR      r0, [r5]
	STR      r1, [r5]
	STR      r0, [r4]
|loc_080531CE|
	ADD      r1, r7, #0
	ADD      r0, r5, #0
	BL       |loc_08052EE0|
	CMP      r0, #0
	BEQ      |loc_080531E2|
	LDR      r1, [r7]
	LDR      r0, [r5]
	STR      r1, [r5]
	STR      r0, [r7]
|loc_080531E2|
	ADD      r6, r5, #0
	ADD      r4, r7, #0
	B        |loc_080531FE|
|loc_080531E8|
	ADD      r1, r7, #0
	ADD      r0, r5, #0
	BL       |loc_08052EE0|
	CMP      r0, #0
	BEQ      |loc_080531FC|
	LDR      r1, [r7]
	LDR      r0, [r5]
	STR      r1, [r5]
	STR      r0, [r7]
|loc_080531FC|
	POP      {r4, r5, r6, r7, pc}
|loc_080531FE|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_08052EE0|
	CMP      r0, #0
	BEQ      |loc_08053218|
|loc_0805320A|
	SUB      r4, #4
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_08052EE0|
	CMP      r0, #0
	BNE      |loc_0805320A|
|loc_08053218|
	ADD      r6, #4
	CMP      r6, r4
	BCS      |sub_08053238|
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	BL       |loc_08052EE0|
	CMP      r0, #0
	BNE      |loc_08053218|
	ADD      r0, r4, #0
	LDR      r2, [r0]
	LDR      r1, [r6]
	STR      r2, [r6]
	STR      r1, [r0]
	SUB      r4, #4
	B        |loc_080531FE|
