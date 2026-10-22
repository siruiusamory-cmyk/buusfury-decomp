	CODE16
|loc_080046AE|
	MOV      r2, #0x13
	LSL      r2, r2, #6
	ADD      r2, r0, r2
	PUSH     {r4}
	LDR      r3, [r2, #0x1c]
	CMP      r3, #0
	BEQ      |loc_080046F0|
	LDR      r3, [r1, #0x14]
	LDR      r4, [r2, #0x20]
	ADD      r3, r3, r4
	STR      r3, [r1, #0x14]
	LDR      r3, [r1, #0x18]
	LDR      r4, [r2, #0x24]
	ADD      r3, r3, r4
	STR      r3, [r1, #0x18]
	LDR      r3, [r1, #0x1c]
	LDR      r4, [r2, #0x28]
	ADD      r3, r3, r4
	STR      r3, [r1, #0x1c]
	LDR      r3, [r1, #0x20]
	LDR      r4, [r2, #0x28]
	ADD      r3, r3, r4
	STR      r3, [r1, #0x20]
	LDR      r3, [r1, #0x24]
	LDR      r2, [r2, #0x2c]
	ADD      r2, r3, r2
	STR      r2, [r1, #0x24]
	MOV      r2, #0x4f
	LSL      r2, r2, #4
	ADD      r1, #0x28
	ADD      r0, r0, r2
	LDRB     r0, [r0]
	STRB     r0, [r1]
|loc_080046F0|
	POP      {r4}
	BX       lr
