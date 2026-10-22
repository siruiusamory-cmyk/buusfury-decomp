	CODE16
|sub_08040A54|
	STMIA    r0!, {r0}
	LSL      r0, r0, #0
	MOV      r0, sp
	ADD      r0, #0xa6
	ADD      r1, sp, #0xa8
	LDRH     r1, [r1]
	STRH     r1, [r0]
	ADD      r2, sp, #0xa4
	LDRH     r0, [r2]
	CMP      r0, #0
	BNE      |loc_080409E8|
	MOV      r0, #0xd0
	LSL      r0, r0, #0x14
	MOV      r1, #1
	LDRH     r0, [r0]
	AND      r1, r0
	CMP      r1, #0
	BEQ      |loc_080409E8|
	LDRH     r0, [r2]
	ADD      r0, #1
	STRH     r0, [r2]
	CMP      r7, #0
	BNE      |loc_080409E8|
	ADD      r0, r5, #0
|loc_08040A84|
	ADD      sp, #0xb0
	POP      {r4, r5, r6, r7}
	POP      {r1}
	BX       r1
