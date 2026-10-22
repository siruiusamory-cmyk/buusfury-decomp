	CODE16
|sub_0800F9A2|
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r0, r1, #0
	MOV      r1, #0x29
	LSL      r1, r1, #4
	ADD      r1, r3, r1
	LDRB     r1, [r1, #1]
	CMP      r1, #0
	BNE      |loc_0800F9C0|
	LDR      r1, [pc, #0x328]
	LDR      r1, [r1, #8]
	ADD      r1, #0x80
	LDR      r1, [r1, #0x30]
	BL       |loc_08009930|
|loc_0800F9C0|
	POP      {r3, pc}
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	ADD      r1, r2, #0
	MOV      r2, #0x29
	LSL      r2, r2, #4
	ADD      r1, r1, r2
	PUSH     {r3, lr}
	LDRB     r1, [r1, #1]
	CMP      r1, #0
	BNE      |loc_0800F9E6|
	LDR      r1, [pc, #0x308]
	LDR      r1, [r1, #8]
	ADD      r1, #0x80
	LDR      r1, [r1, #0x30]
	BL       |loc_08009324|
	CMP      r0, #0
	BEQ      |sub_0800F9EA|
|loc_0800F9E6|
	MOV      r0, #1
	POP      {r3, pc}
