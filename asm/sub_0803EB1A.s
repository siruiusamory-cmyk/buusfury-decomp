	CODE16
|sub_0803EB1A|
	LDRB     r1, [r4, #0xa]
	LSL      r2, r1, #0x1c
	BMI      |loc_0803EB34|
	CMP      r6, #0
	BEQ      |loc_0803EB34|
	CMP      r6, #1
	BEQ      |sub_0803EB4C|
	CMP      r6, #2
	BNE      |loc_0803EB34|
	LDR      r2, [pc, #0x264]
	ORR      r1, r0
	STR      r2, [r5, #0x54]
	STRB     r1, [r4, #0xa]
|loc_0803EB34|
	LDR      r1, [r5, #0x44]
	LDR      r2, [r5, #0x40]
	CMP      r1, r2
	BLS      |sub_0803EB56|
	LDR      r2, [pc, #0x258]
	LSL      r1, r6, #2
	LDR      r1, [r2, r1]
	STR      r1, [r5, #0x54]
	LDRB     r1, [r4, #0xa]
	ORR      r0, r1
	STRB     r0, [r4, #0xa]
	POP      {r4, r5, r6, r7, pc}
