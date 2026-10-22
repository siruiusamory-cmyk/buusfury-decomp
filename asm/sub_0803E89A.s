	CODE16
|sub_0803E89A|
	LDR      r3, [pc, #0x1bc]
	STR      r3, [r0, #0x54]
	LDRB     r3, [r1, #0xa]
	ORR      r3, r4
	STRB     r3, [r1, #0xa]
	MOV      r3, #0x44
	AND      r5, r3
	BEQ      |loc_0803E8B8|
	LDRB     r2, [r2, #0xc]
	STRB     r2, [r1, #8]
	STRB     r2, [r0, #0x12]
	LDRB     r1, [r0, #0x10]
	MOV      r2, #0x10
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
|loc_0803E8B8|
	POP      {r4, r5, r6}
	BX       lr
