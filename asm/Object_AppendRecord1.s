	CODE16
|Object_AppendRecord1|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	ADD      r0, #0x4c
	LDR      r3, [r0]
	ADD      r4, r3, #1
	ADD      r6, r3, #0
	LSL      r3, r6, #1
	ADD      r3, r3, r6
	LSL      r3, r3, #2
	STR      r4, [r0]
	ADD      r4, r3, r0
	ADD      r4, #4
	STMIA    r4!, {r1, r2}
	LDR      r0, [pc, #0x1ec]
	SUB      r4, #8
	LDR      r0, [r0, #4]
	BL       |inc_0x03d784_0x041118| + 0x2864
	STR      r0, [r4, #8]
	MOV      r0, #0
	ADD      r5, #0xff
	ADD      r5, #1
	STR      r0, [r5, #0x10]
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r5, [r4, #0x4c]
	MOV      r0, #0
	CMP      r5, #0
	BLE      |loc_08016076|
	ADD      r2, r4, #0
	ADD      r2, #0x4c
	LSL      r3, r0, #1
	ADD      r3, r3, r0
	LSL      r3, r3, #2
	ADD      r3, r3, r2
	LDR      r3, [r3, #4]
	CMP      r3, r1
	BNE      |sub_08016078|
	LDR      r1, [r2]
	SUB      r1, #1
	STR      r1, [r2]
	SUB      r1, r1, r0
	BEQ      |loc_0801606E|
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r5, r1, #1
	ADD      r5, r5, r1
	LSL      r0, r0, #2
	ADD      r0, r0, r2
	ADD      r1, r0, #0
	ADD      r1, #0x10
	ADD      r0, #4
	LSL      r5, r5, #2
	ADD      r2, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801606E|
	MOV      r0, #0
	ADD      r4, #0xff
	ADD      r4, #1
	STR      r0, [r4, #0x10]
|loc_08016076|
	POP      {r3, r4, r5, pc}
