	CODE16
|sub_08042C40|
	LSL      r2, r0, #5
	ADD      r2, r2, r3
	LDRH     r2, [r2, #0x14]
	CMP      r2, r4
	BEQ      |loc_08042C54|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r1, r0
	BHI      |sub_08042C40|
|loc_08042C54|
	CMP      r1, #0
	BEQ      |loc_08042C5C|
	CMP      r1, r0
	BNE      |sub_08042C6C|
|loc_08042C5C|
	MOV      r0, #3
	STRH     r0, [r5, #0x14]
	MOV      r1, #1
	MOV      r0, #0xf3
	BL       |loc_0804333c|
	MOV      r0, #3
	POP      {r4, r5, r6, pc}
