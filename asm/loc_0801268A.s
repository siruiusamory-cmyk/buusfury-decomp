	CODE16
|loc_0801268A|
	PUSH     {r4, lr}
	LDR      r2, [r0]
	ADD      r4, r1, #0
	MOV      r1, #0
	CMP      r2, #0
	BLE      |loc_080126A6|
|loc_08012696|
	LSL      r3, r1, #2
	ADD      r3, r3, r0
	LDR      r3, [r3, #4]
	CMP      r3, r4
	BEQ      |loc_080126AA|
	ADD      r1, #1
	CMP      r2, r1
	BGT      |loc_08012696|
|loc_080126A6|
	MOV      r1, #0
	MVN      r1, r1
|loc_080126AA|
	SUB      r2, #1
	STR      r2, [r0]
	SUB      r2, r2, r1
	BEQ      |loc_080126C2|
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	ADD      r1, r0, #0
	ADD      r1, #8
	LSL      r2, r2, #2
	ADD      r0, #4
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080126C2|
	ADD      r0, r4, #0
	BEQ      |loc_080126D2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080126D2|
	POP      {r4, pc}
