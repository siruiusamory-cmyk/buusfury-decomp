	CODE16
|sub_0803DAE8|
	LDRH     r0, [r5]
	CMP      r0, #0
	BEQ      |loc_0803DAF2|
	CMP      r0, #0xa
	BNE      |sub_0803DAE6|
|loc_0803DAF2|
	SUB      r0, r5, r7
	ASR      r6, r0, #1
	BEQ      |loc_0803DB5E|
	ADD      r2, r6, #0
	ADD      r1, r7, #0
	LDR      r0, [r4, #0xc]
	BL       |loc_0804001A|
	LDR      r1, [r4, #8]
	SUB      r1, #0xc
	STR      r1, [sp, #8]
	LDRB     r1, [r4]
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1e
	BEQ      |sub_0803DB20|
	CMP      r1, #1
	BEQ      |loc_0803DB32|
	CMP      r1, #2
	BNE      |loc_0803DB3C|
	LDR      r1, [r4, #4]
	SUB      r0, r1, r0
	STR      r0, [sp, #4]
	B        |loc_0803DB3C|
