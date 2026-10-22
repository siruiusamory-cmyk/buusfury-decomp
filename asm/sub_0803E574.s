	CODE16
|sub_0803E574|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	ADD      r4, #0x50
	LDR      r1, [pc, #0x228]
	LDRB     r0, [r4, #0xe]
	SUB      r1, #4
	LDR      r1, [r1]
	STRB     r0, [r1, #3]
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	LDR      r0, [pc, #0x214]
	ADD      r4, #0x50
	SUB      r0, #4
	LDR      r1, [r0]
	LDR      r2, [r0]
	LDRB     r1, [r1, #2]
	ADD      r1, #0xff
	STRB     r1, [r2, #1]
	LDRB     r1, [r4, #0xe]
	LDR      r0, [r0]
	SUB      r1, #1
	STR      r1, [r0, #0x10]
	POP      {r4, pc}
