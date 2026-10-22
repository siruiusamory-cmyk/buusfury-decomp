	CODE16
|sub_0803EF82|
	ADD      r1, r3, #0
	ADD      r1, #0x50
	LDRB     r2, [r1, #8]
	LSL      r3, r2, #0x1f
	BPL      |loc_0803EF96|
	LDR      r3, [r0, #0x14]
	ADD      r4, r3, #1
	STR      r4, [r0, #0x14]
	LDRB     r3, [r3]
	STRB     r3, [r1, #0xa]
|loc_0803EF96|
	LSL      r3, r2, #0x1e
	BPL      |loc_0803EFA4|
	LDR      r3, [r0, #0x14]
	ADD      r4, r3, #1
	STR      r4, [r0, #0x14]
	LDRB     r3, [r3]
	STRB     r3, [r1, #0xb]
|loc_0803EFA4|
	LSL      r3, r2, #0x1d
	BPL      |loc_0803EFB2|
	LDR      r3, [r0, #0x14]
	ADD      r4, r3, #1
	STR      r4, [r0, #0x14]
	LDRB     r3, [r3]
	STRB     r3, [r1, #0xc]
|loc_0803EFB2|
	LSL      r2, r2, #0x1c
	BPL      |loc_0803EF34|
	LDR      r2, [r0, #0x14]
	ADD      r3, r2, #1
	STR      r3, [r0, #0x14]
	LDRB     r2, [r2]
	STRB     r2, [r1, #0xd]
	LDR      r2, [r0, #0x14]
	ADD      r3, r2, #1
	STR      r3, [r0, #0x14]
	LDRB     r2, [r2]
	STRB     r2, [r1, #0xe]
	B        |loc_0803EF34|
