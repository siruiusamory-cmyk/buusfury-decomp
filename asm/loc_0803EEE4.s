	CODE16
|loc_0803EEE4|
	PUSH     {r4}
	LDRB     r1, [r0, #1]
	MOV      r2, #0
	ADD      r1, #1
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	STRB     r1, [r0, #1]
	LDRB     r3, [r0, #2]
	CMP      r1, r3
	BCC      |loc_0803EF20|
	LDR      r3, [r0, #0x10]
	ADD      r3, #1
	STR      r3, [r0, #0x10]
	LDR      r1, [r0, #0xc]
	LDR      r4, [r1, #4]
	LDRB     r3, [r4, r3]
	CMP      r3, #0xff
	BNE      |loc_0803EF0A|
	STR      r2, [r0, #0x10]
|loc_0803EF0A|
	LDR      r3, [r1, #4]
	LDR      r4, [r0, #0x10]
	LDR      r1, [r1]
	LDRB     r3, [r3, r4]
	LSL      r3, r3, #2
	LDR      r1, [r1, r3]
	STRB     r2, [r0, #1]
	ADD      r3, r1, #1
	STR      r3, [r0, #0x14]
	LDRB     r1, [r1]
	STRB     r1, [r0, #2]
|loc_0803EF20|
	MOV      r1, #0
|loc_0803EF22|
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #5
	ADD      r3, r3, r0
	ADD      r3, #0x70
	ADD      r1, #1
	CMP      r1, #0xf
	STRB     r2, [r3]
	BLT      |loc_0803EF22|
|loc_0803EF34|
	LDR      r1, [r0, #0x14]
	ADD      r2, r1, #1
	STR      r2, [r0, #0x14]
	LDRB     r1, [r1]
	CMP      r1, #0
	BEQ      |sub_0803EFCC|
	LSL      r3, r1, #0x1c
	LSR      r3, r3, #0x1c
	SUB      r4, r3, #1
	LSL      r3, r4, #1
	ADD      r3, r3, r4
	LSL      r3, r3, #5
	ADD      r3, r3, r0
	ADD      r3, #0x18
	LSR      r1, r1, #4
	CMP      r1, #0
	BNE      |sub_0803EF66|
	ADD      r1, r2, #1
	STR      r1, [r0, #0x14]
	LDRB     r2, [r2]
	ADD      r1, r3, #0
	ADD      r1, #0x50
	STRB     r2, [r1, #9]
	STRB     r2, [r1, #8]
	B        |sub_0803EF82|
