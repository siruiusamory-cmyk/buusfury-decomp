	CODE16
|sub_08012C4A|
	MOV      r0, #0
	STR      r0, [r7, #0x44]
	LDR      r0, [r4, #8]
	LDR      r1, [r0, #0x40]
	CMP      r1, #0
	BNE      |loc_08012C90|
	LDR      r0, [r0, #0x44]
	CMP      r0, #0
	BNE      |loc_08012C90|
	LDR      r1, [r5]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r5, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x17
	LSR      r0, r0, #0x1f
	BEQ      |sub_08012C80|
	LDR      r0, [pc, #0x9c]
	LDR      r1, [r4, #8]
	LDR      r0, [r0, #4]
	BL       |loc_08011944|
	STR      r6, [r4, #8]
	POP      {r3, r4, r5, r6, r7, pc}
