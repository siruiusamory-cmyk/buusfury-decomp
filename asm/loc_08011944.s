	CODE16
|loc_08011944|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r1, #0
	MOV      r1, #0
	LDR      r3, [r0, #4]
	ADD      r6, r0, #4
	ADD      r5, r0, #0
	MVN      r0, r1
	CMP      r3, #0
	BLE      |loc_08011966|
|loc_08011956|
	LSL      r2, r1, #2
	ADD      r2, r2, r6
	LDR      r2, [r2, #4]
	CMP      r2, r4
	BEQ      |loc_08011968|
	ADD      r1, #1
	CMP      r3, r1
	BGT      |loc_08011956|
|loc_08011966|
	ADD      r1, r0, #0
|loc_08011968|
	LDR      r7, [pc, #0x12c]
	ADD      r3, r1, #1
	BEQ      |sub_0801197E|
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x6d34
	LDR      r0, [r5, #4]
	LSL      r0, r0, #2
	ADD      r0, r0, r6
	STR      r7, [r0, #4]
	B        |loc_080119AE|
