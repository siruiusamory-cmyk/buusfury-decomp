	CODE16
|loc_0800A9D0|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0x30]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_0800A9F8|
	ADD      r6, r5, #0
	ADD      r6, #0x30
|loc_0800A9E0|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r5, #0x30]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_0800A9E0|
|loc_0800A9F8|
	MOV      r0, #0
	STR      r0, [r5, #0x30]
	POP      {r4, r5, r6, pc}
