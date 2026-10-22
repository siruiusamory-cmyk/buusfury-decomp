	CODE16
|sub_080089FC|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |loc_080125E0|
	MOV      r2, #0
	CMP      r0, #0
	LDR      r1, [pc, #0x4c]
	BLE      |loc_08008A26|
	LDRB     r3, [r1]
	CMP      r3, r4
	BNE      |sub_08008A1E|
	LDRB     r3, [r1, #1]
	CMP      r3, r5
	BNE      |sub_08008A1E|
	ADD      r0, r1, #0
	POP      {r3, r4, r5, pc}
