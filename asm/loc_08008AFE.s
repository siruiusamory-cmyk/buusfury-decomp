	CODE16
|loc_08008AFE|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	LDR      r0, [r0, #4]
	MOV      r4, #0
	LDRB     r0, [r0, #5]
	CMP      r0, #0
	BLE      |loc_08008B2E|
|loc_08008B0C|
	LDR      r0, [r6, #4]
	LSL      r1, r4, #2
	LDR      r0, [r0, #0x18]
	LDR      r5, [r0, r1]
	LDR      r0, [r5]
	BL       |loc_08004784|
	CMP      r0, #0
	BEQ      |loc_08008B24|
	ADD      r0, r5, #0
	BL       |loc_0800C7E2|
|loc_08008B24|
	LDR      r0, [r6, #4]
	ADD      r4, #1
	LDRB     r0, [r0, #5]
	CMP      r0, r4
	BGT      |loc_08008B0C|
|loc_08008B2E|
	POP      {r4, r5, r6, pc}
