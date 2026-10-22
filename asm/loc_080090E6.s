	CODE16
|loc_080090E6|
	PUSH     {r4, lr}
	LDR      r0, [r0, #4]
	LDRB     r4, [r0, #6]
	CMP      r4, r1
	BLE      |loc_08009106|
	LDR      r0, [r0, #0x1c]
	LSL      r1, r1, #2
	LDR      r1, [r0, r1]
	MOV      r0, #0
	BL       |loc_0800DCDC|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xfc]
	LDR      r0, [r0, #0x14]
	BL       |List_Append|
|loc_08009106|
	POP      {r4, pc}
