	CODE16
|loc_0803DD66|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	ADD      r6, r2, #0
	SUB      r0, #0xc
	SUB      sp, #8
	STR      r0, [sp, #4]
	LDR      r0, [sp, #4]
	LDR      r1, [r4, #0x1c]
	CMP      r0, r1
	BGE      |loc_0803DE4C|
|loc_0803DD7C|
	LDRH     r0, [r6]
	CMP      r0, #0
	BEQ      |loc_0803DE4C|
	CMP      r0, #0x20
	BNE      |sub_0803DD8A|
	ADD      r6, #2
	B        |loc_0803DD7C|
