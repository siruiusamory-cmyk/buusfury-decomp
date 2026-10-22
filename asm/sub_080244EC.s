	CODE16
|sub_080244EC|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x41
	LDR      r0, [r6]
	CMP      r0, #0
	BEQ      |sub_08024528|
	CMP      r0, #1
	BEQ      |loc_08024532|
	CMP      r0, #2
	BEQ      |loc_08024548|
	CMP      r0, #3
	BNE      |loc_08024512|
	LDRB     r1, [r4, #1]
	MOV      r0, #1
	CMP      r1, #0
	BNE      |loc_0802450E|
	MOV      r0, #0
|loc_0802450E|
	LDR      r1, [pc, #0x5c]
	STR      r0, [r1, #4]
|loc_08024512|
	LDRB     r0, [r4]
	LDR      r1, [pc, #0x54]
	STR      r0, [r1]
	MOV      r0, #1
	STR      r0, [r5, #0x3c]
	LDRB     r2, [r4, #1]
	CMP      r2, #0
	BNE      |loc_08024524|
	MOV      r0, #0
|loc_08024524|
	STR      r0, [r1, #4]
	POP      {r4, r5, r6, pc}
