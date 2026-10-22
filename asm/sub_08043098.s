	CODE16
|sub_08043098|
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x2b8]
	MOV      r2, #5
	LDRB     r3, [r4, #7]
	MOV      r1, #1
	CMP      r3, #5
	BNE      |loc_080430BA|
	STRB     r1, [r4, #6]
	STRB     r2, [r4, #4]
	LDRH     r3, [r4, #0x1c]
	STRH     r3, [r4, #0x1a]
	CMP      r3, #0
	BEQ      |loc_080430B8|
	MOV      r3, #6
	STRB     r3, [r4, #7]
	B        |loc_080430BA|
|loc_080430B8|
	STRB     r1, [r4, #7]
|loc_080430BA|
	LDRB     r3, [r4, #7]
	CMP      r3, #1
	BNE      |sub_080430E8|
	STRB     r1, [r4, #6]
	ADD      r1, r0, #0
	MOV      r0, #0x8c
	STRB     r2, [r4, #4]
	BL       |inc_0x046118_0x049114| + 0xe18
	LSL      r0, r1, #0x10
	LSR      r0, r0, #0x10
	MOV      r1, #0x8c
	SUB      r1, r1, r0
	STRH     r0, [r4, #0x1a]
	STRH     r1, [r4, #0x1c]
	CMP      r0, #0
	BEQ      |sub_080430E2|
	MOV      r0, #2
	STRB     r0, [r4, #7]
|loc_080430E0|
	POP      {r4, pc}
