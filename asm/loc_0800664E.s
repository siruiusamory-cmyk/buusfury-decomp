	CODE16
|loc_0800664E|
	PUSH     {r3, lr}
	ADD      r0, #4
	LDR      r2, [r0]
	ADD      r3, r2, #1
	STR      r3, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	STR      r1, [r0, #4]
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	BEQ      |loc_080066B8|
	ADD      r1, r0, #4
	LDR      r3, [r1]
	MOV      r0, #0
	CMP      r3, #0
	BLE      |loc_0800668C|
|loc_0800667C|
	LSL      r2, r0, #2
	ADD      r2, r2, r1
	LDR      r2, [r2, #4]
	CMP      r2, r4
	BEQ      |loc_08006690|
	ADD      r0, #1
	CMP      r3, r0
	BGT      |loc_0800667C|
|loc_0800668C|
	MOV      r0, #0
	MVN      r0, r0
|loc_08006690|
	SUB      r3, #1
	STR      r3, [r1]
	SUB      r2, r3, r0
	BEQ      |loc_080066A8|
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	ADD      r1, r0, #0
	ADD      r1, #8
	LSL      r2, r2, #2
	ADD      r0, #4
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080066A8|
	ADD      r0, r4, #0
	BEQ      |loc_080066B8|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080066B8|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_080066E6|
	ADD      r6, r5, #4
|loc_080066C8|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_080066DE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080066DE|
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_080066C8|
|loc_080066E6|
	MOV      r0, #0
	STR      r0, [r5, #4]
	POP      {r4, r5, r6, pc}
