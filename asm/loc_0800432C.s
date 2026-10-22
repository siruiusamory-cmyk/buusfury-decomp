	CODE16
|loc_0800432C|
	MOV      r2, #0x13
	LSL      r2, r2, #6
	LDR      r1, [pc, #0x204]
	ADD      r0, r0, r2
	LDR      r2, [r0, #0x10]
	LDR      r1, [r1, #4]
	SUB      r1, r2, r1
	STR      r1, [r0, #0x10]
	BX       lr
	PUSH     {r4}
	ADD      r2, r0, #0
	MOV      r0, #0
	MOV      r4, #0x9f
	MOV      r1, #0
	LSL      r4, r4, #3
|loc_0800434A|
	MOV      r3, #0x68
	MUL      r3, r1
	ADD      r3, r3, r2
	ADD      r3, r3, r4
	LDRB     r3, [r3]
	ADD      r1, #1
	LSL      r3, r3, #0x1f
	LSR      r3, r3, #0x1f
	ADD      r0, r3, r0
	CMP      r1, #8
	BLT      |loc_0800434A|
	POP      {r4}
	BX       lr
