	CODE16
|loc_08004764|
	PUSH     {r3, lr}
	LDRB     r1, [r0, #1]
	LSL      r2, r1, #0x1e
	LSR      r2, r2, #0x1f
	BEQ      |loc_08004782|
	MOV      r2, #2
	BIC      r1, r2
	STRB     r1, [r0, #1]
	LDR      r0, [pc, #0x98]
	MOV      r1, #0x15
	MOV      r2, #0
	SUB      r0, #0x14
	LDR      r0, [r0, #0x10]
	BL       |List_CallMethod1|
|loc_08004782|
	POP      {r3, pc}
