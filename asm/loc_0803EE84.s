	CODE16
|loc_0803EE84|
	ADD      r1, r0, #0
	ADD      r1, #0x40
	PUSH     {r3, lr}
	LDRB     r2, [r1, #0xa]
	LSR      r2, r2, #2
	LSL      r2, r2, #2
	STRB     r2, [r1, #0xa]
	LSL      r1, r2, #0x1d
	BPL      |loc_0803EEA8|
	LDR      r1, [r0, #0x40]
	LDR      r2, [r0, #0x30]
	CMP      r2, r1
	BEQ      |loc_0803EEA8|
	STR      r1, [r0, #0x30]
	LDRB     r1, [r0, #0x10]
	MOV      r2, #2
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
|loc_0803EEA8|
	ADD      r1, r0, #0
	ADD      r1, #0x50
	LDRB     r2, [r1, #8]
	CMP      r2, #0
	BEQ      |loc_0803EEC6|
	MOV      r3, #0x88
	AND      r2, r3
	LDRB     r1, [r1, #0xd]
	BNE      |loc_0803EEBC|
	MOV      r1, #0
|loc_0803EEBC|
	LDR      r2, [pc, #0x194]
	LSL      r1, r1, #2
	LDR      r1, [r2, r1]
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0803EEC6|
	POP      {r3, pc}
	PUSH     {r3, lr}
	MOV      r1, #0x4a
	LDRB     r2, [r1, r0]
	LSL      r1, r2, #0x1e
	LSR      r1, r1, #0x1e
	BEQ      |loc_0803EEE2|
	CMP      r1, #1
	BNE      |loc_0803EEDC|
	LSL      r1, r2, #0x1d
	BPL      |loc_0803EEE2|
|loc_0803EEDC|
	LDR      r1, [r0, #0x54]
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0803EEE2|
	POP      {r3, pc}
