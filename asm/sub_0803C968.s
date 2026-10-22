	CODE16
|sub_0803C968|
	LDRB     r0, [r4, #0x10]
	CMP      r0, #0
	BEQ      |loc_0803C992|
	CMP      r0, #1
	BEQ      |loc_0803C99E|
	CMP      r0, #2
	BEQ      |sub_0803C986|
	CMP      r0, #3
	BNE      |loc_0803C9A6|
	LDR      r0, [sp, #0x44]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #0x54]
	ADD      r0, #3
	STR      r0, [sp, #0xc]
	B        |loc_0803C9A6|
