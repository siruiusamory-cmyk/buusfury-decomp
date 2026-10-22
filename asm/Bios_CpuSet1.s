	CODE16
|Bios_CpuSet1|
	CMP      r4, #3
	BNE      |loc_080428D0|
	LDR      r5, [pc, #0x328]
	LDRB     r0, [r5, #0xf]
	CMP      r0, #0
	BEQ      |loc_080428D0|
	CMP      r6, #0x24
	BEQ      |loc_08042898|
	CMP      r6, #0x26
	BEQ      |loc_08042898|
	CMP      r6, #0x27
	BNE      |loc_080428D0|
|loc_08042898|
	BL       |inc_0x042118_0x049114| + 0x179a
	BL       |loc_0804389e|
	ADD      r0, sp, #8
	BL       |inc_0x042118_0x049114| + 0x17ac
	ADD      r3, sp, #0
	LDRB     r0, [r3, #8]
	CMP      r0, #0
	BNE      |loc_080428D0|
	LDR      r5, [pc, #0x2fc]
	LDR      r0, [r5]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |loc_080428D0|
	BL       |loc_08043800|
	LDR      r1, [r5]
	ADD      r0, #4
	LDRB     r1, [r1, #2]
	MOV      r7, #1
	STRB     r1, [r0]
	STRB     r7, [r0, #1]
	MOV      r0, #0x29
	BL       |loc_08042372|
	MOV      r4, #0
|loc_080428D0|
	CMP      r6, #0x10
	BEQ      |loc_080428E0|
	CMP      r6, #0x26
	BEQ      |loc_080429A4|
	CMP      r6, #0x30
	BEQ      |sub_08042904|
	CMP      r6, #0x3d
	BNE      |loc_080429C4|
|loc_080428E0|
	CMP      r4, #0
	BNE      |loc_080429C6|
	LDR      r5, [pc, #0x2c8]
	MOV      r7, #0xff
	STRB     r4, [r5, #0xd]
	STRB     r4, [r5, #1]
	STRB     r4, [r5]
	STRB     r7, [r5, #6]
	BL       |sub_08043368|
	CMP      r6, #0x3d
	BNE      |loc_080429C8|
	ADD      r3, sp, #0
	STRH     r4, [r3, #4]
	SWI      0xb
	STRB     r7, [r5, #6]
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
