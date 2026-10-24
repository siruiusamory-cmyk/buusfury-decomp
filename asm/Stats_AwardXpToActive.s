	CODE16
|Stats_AwardXpToActive|
	PUSH     {r3, lr}
	LDRB     r2, [r0]
	MOV      r3, #0x68
	MUL      r2, r3
	ADD      r0, r2, r0
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r0, r0, r2
	BL       |Stats_AwardXpIfAlive|
	POP      {r3, pc}
	PUSH     {r4, r5, r6}
	ADD      r3, r0, #0
	ADD      r5, r3, #0
	ADD      r5, #0xe4
	LDR      r6, [r5]
	MOV      r0, #0
	MOV      r2, #0
	CMP      r6, #0
	BLE      |loc_0800441A|
|loc_08004400|
	LSL      r3, r2, #2
	ADD      r3, r3, r5
	LDR      r3, [r3, #4]
	LSL      r4, r3, #4
	LSR      r4, r4, #4
	CMP      r4, r1
	BNE      |loc_08004414|
	LSR      r3, r3, #0x1c
	BNE      |loc_08004414|
	ADD      r0, #1
|loc_08004414|
	ADD      r2, #1
	CMP      r6, r2
	BGT      |loc_08004400|
|loc_0800441A|
	POP      {r4, r5, r6}
	BX       lr
