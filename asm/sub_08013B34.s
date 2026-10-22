	CODE16
|sub_08013B34|
	LDRB     r2, [r0, #0xc]
	CMP      r2, #0
	BNE      |loc_08013B3E|
	MOV      r0, #0
	BX       lr
|loc_08013B3E|
	LDRB     r1, [r0, #0x15]
	ADD      r1, #1
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	STRB     r1, [r0, #0x15]
	CMP      r1, r2
	BCC      |loc_08013B50|
	MOV      r1, #0
	STRB     r1, [r0, #0x15]
|loc_08013B50|
	MOV      r0, #1
	BX       lr
