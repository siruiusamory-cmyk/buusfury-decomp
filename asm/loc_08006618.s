	CODE16
|loc_08006618|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x24c]
	MOV      r4, #0
	STR      r0, [r5]
	LDR      r0, [r5, #4]
	CMP      r0, #0
	BLE      |loc_08006648|
	ADD      r6, r5, #4
|loc_0800662A|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_08006640|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08006640|
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_0800662A|
|loc_08006648|
	LDR      r0, [pc, #0x224]
	STR      r0, [r5]
	POP      {r4, r5, r6, pc}
