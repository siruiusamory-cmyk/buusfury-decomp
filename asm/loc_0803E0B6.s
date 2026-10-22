	CODE16
|loc_0803E0B6|
	PUSH     {r4}
	LDRB     r1, [r0, #0x10]
	LSL      r2, r1, #0x1f
	BPL      |loc_0803E14E|
	LSL      r2, r1, #0x1b
	BPL      |sub_0803E0F6|
	MOV      r2, #0x34
	LDRB     r2, [r2, r0]
	LDRB     r3, [r0, #0x12]
	MUL      r2, r3
	MOV      r3, #0x13
	LDRSB    r4, [r0, r3]
	MOV      r3, #0x40
	SUB      r3, r3, r4
	ADD      r4, #0x40
	MUL      r3, r2
	ASR      r3, r3, #0xa
	LSL      r3, r3, #0x10
	MUL      r4, r2
	ASR      r2, r4, #0xa
	LSR      r3, r3, #0x10
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	STRH     r3, [r0, #0xc]
	STRH     r2, [r0, #0xe]
	ORR      r2, r3
	BNE      |sub_0803E0F2|
	LDR      r2, [pc, #0x278]
	STR      r2, [r0, #0x18]
	B        |sub_0803E0F6|
