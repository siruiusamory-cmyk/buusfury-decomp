	CODE16
|sub_080332E0|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080332FC|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080332FC|
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	POP      {r3, r4, r5, r7, pc}
	LSR      r4, r0, #0x20
	PUSH     {lr}
	ADD      r2, r1, #0
	LDR      r1, [r0, #4]
	MOV      r0, #0x85
	LSL      r0, r0, #2
	ADD      r2, r2, r0
	MOV      r0, #0
	SUB      sp, #0x6c
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	LDR      r0, [sp]
	CMP      r0, #1
	BNE      |loc_08033338|
	LDR      r0, [sp, #4]
	CMP      r0, #0
	BEQ      |sub_08033334|
	MOV      r0, #1
	ADD      sp, #0x6c
	POP      {pc}
