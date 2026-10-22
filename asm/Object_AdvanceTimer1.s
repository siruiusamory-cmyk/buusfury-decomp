	CODE16
|Object_AdvanceTimer1|
	ADD      r1, r0, #0
	ADD      r1, #0x40
	LDRB     r2, [r1, #8]
	LDRB     r3, [r1, #0xb]
	SUB      r2, r2, r3
	LSL      r2, r2, #0x18
	ASR      r2, r2, #0x18
	STRB     r2, [r1, #8]
	CMP      r2, #0
	BGT      |loc_0803E5CC|
	MOV      r2, #0
	STRB     r2, [r1, #8]
	LDRB     r2, [r1, #0xa]
	LSR      r2, r2, #2
	LSL      r2, r2, #2
	STRB     r2, [r1, #0xa]
|loc_0803E5CC|
	LDRB     r1, [r1, #8]
	MOV      r2, #0x10
	STRB     r1, [r0, #0x12]
	LDRB     r1, [r0, #0x10]
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	BX       lr
