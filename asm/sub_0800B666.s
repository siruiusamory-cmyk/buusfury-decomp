	CODE16
|sub_0800B666|
	PUSH     {r4, lr}
	LDR      r4, [r2, #0xc]
	MOV      r3, #0x68
	LDRB     r1, [r4]
	MUL      r1, r3
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r1, r1, r4
	ADD      r1, r1, r3
	LDR      r3, [r1, #8]
	CMP      r3, #0
	BLT      |loc_0800B692|
	LDRB     r1, [r1, #0x14]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r3, [pc, #0x18c]
	LSL      r1, r1, #3
	ADD      r1, r1, r3
	LDRB     r1, [r1]
	LSL      r1, r1, #0x1c
	LSR      r1, r1, #0x1f
	BNE      |sub_0800B69E|
|loc_0800B692|
	ADD      r1, r0, #0
	LDR      r0, [r2, #8]
	BL       |loc_08011944|
	MOV      r0, #0
	POP      {r4, pc}
