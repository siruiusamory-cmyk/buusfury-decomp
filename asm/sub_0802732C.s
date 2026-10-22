	CODE16
|sub_0802732C|
	PUSH     {r3, lr}
	BL       |inc_0x0158_0x143f2| + 0xede0
	MOV      r0, #1
|loc_08027334|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |inc_0x0158_0x143f2| + 0xedb0
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0x81
	LDR      r1, [r0, #0x14]
	ADD      r1, #1
	STR      r1, [r0, #0x14]
	LSL      r0, r1, #0x17
	LDR      r1, [pc, #0x38]
	LSR      r0, r0, #0x1e
	LDRB     r0, [r1, r0]
	STRB     r0, [r4, #0x10]
	ADD      r0, r4, #0
	BL       |loc_080272AC|
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |sub_0802736A|
	LDR      r1, [pc, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, pc}
