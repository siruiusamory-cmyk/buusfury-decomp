	CODE16
|loc_0803FAAC|
	LDR      r2, [pc, #0xc0]
	LDR      r1, [pc, #0xc4]
	LDR      r0, [r2]
	ADD      r1, r0, r1
	LDR      r0, [r2, #4]
	EOR      r1, r0
	LSL      r3, r0, #3
	LSR      r0, r0, #0x1d
	ORR      r0, r3
	LDR      r3, [pc, #0xb8]
	ADD      r0, r0, r3
	EOR      r0, r1
	STR      r0, [r2, #4]
	STR      r1, [r2]
	SUB      r0, r1, r0
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0803FAAC|
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	MUL      r0, r4
	LSR      r0, r0, #0x10
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0803FAAC|
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	CMP      r0, r4
	BCS      |sub_0803FAF2|
	MOV      r0, #1
	POP      {r4, pc}
