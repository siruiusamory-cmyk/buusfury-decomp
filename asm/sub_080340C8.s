	CODE16
|sub_080340C8|
	MOV      r3, #4
	ADD      r1, r5, #0
	MOV      r0, #0
	LDR      r2, [pc, #0x34]
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r1, r4, #0
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|loc_080340E8|
	DCW      0xce50
	DCW      0x0804,0x05d3,0x0000,0x45a0,0xffff
|loc_080340F4|
	STR      r3, [sp, #0x360]
	LSR      r5, r6, #1
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	ADD      r0, #0x84
	LSR      r0, r7, #1
	STR      r2, [sp, #0x190]
	LSR      r4, r0, #0x20
	BLS      |loc_080340A8|
	LSR      r7, r5, #1
	PUSH     {r3, r4, r5, lr}
	LDRB     r3, [r1, #0x10]
	LDRB     r4, [r2]
	MOV      r5, #1
	EOR      r4, r5
	CMP      r3, r4
	BNE      |sub_08034120|
	LDR      r0, [r0, #0xc]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, r4, r5, pc}
