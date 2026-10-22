	CODE16
|sub_08027932|
	LSR      r4, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	CMP      r7, #0xdc
	LSR      r1, r6, #1
	CMP      r2, #0xaa
	LSL      r0, r0, #0
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x95
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r7
	BNE      |loc_08027960|
	MOV      r0, #0x92
	BL       |inc_0x0158_0x143f2|
	ADD      r7, r0, #0
|loc_08027960|
	MOV      r4, #0
	LDR      r1, [pc, #0x74]
	LSL      r0, r4, #4
	ADD      r6, r0, r1
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r7
	BNE      |loc_08027996|
	CMP      r5, #0
	LDR      r0, [r6, #0xc]
	BEQ      |sub_0802798E|
	CMP      r0, #0
	BLT      |loc_08027996|
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LDR      r6, [pc, #0x58]
	LSL      r0, r0, #2
	ADD      r0, r0, r6
	CMP      r0, r5
	BNE      |loc_08027996|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
