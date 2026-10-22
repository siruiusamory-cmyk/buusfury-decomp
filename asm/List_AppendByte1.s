	CODE16
|List_AppendByte1|
	LDRB     r2, [r0, #0xc]
	ADD      r2, r2, r0
	STRB     r1, [r2, #0xd]
	LDRB     r1, [r0, #0xc]
	LSL      r1, r1, #1
	ADD      r1, r1, r0
	ADD      r1, #0x2e
	MOV      r2, #0
|loc_08013AA0|
	STRB     r2, [r1]
	LDRB     r3, [r1]
	CMP      r3, r2
	BNE      |loc_08013AA0|
	MOV      r2, #0
|loc_08013AAA|
	STRB     r2, [r1, #1]
	LDRB     r3, [r1, #1]
	CMP      r3, r2
	BNE      |loc_08013AAA|
	LDRB     r1, [r0, #0xc]
	ADD      r1, #1
	STRB     r1, [r0, #0xc]
	BX       lr
