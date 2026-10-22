	CODE16
|loc_080066EC|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	ADD      r7, r1, #0
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08006716|
	ADD      r6, r5, #4
|loc_080066FC|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r7, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_080066FC|
|loc_08006716|
	POP      {r3, r4, r5, r6, r7, pc}
