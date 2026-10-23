	CODE16
|sub_080188F4|
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x68]
	ADD      r2, r2, r1
	LDR      r1, [r3, #4]
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801891E|
	LDR      r1, [pc, #0x30]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0801891E|
	POP      {r4, pc}
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x68]
	ADD      r2, r2, r1
	LDR      r1, [r3, #0xc]
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x68]
	ADD      r2, r2, r1
	LDR      r1, [r3, #0xc]
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	POP      {r3, r4, r7}
	LSR      r4, r0, #0x20
