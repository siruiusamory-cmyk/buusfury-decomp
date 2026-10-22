	CODE16
|sub_0803525C|
	MOV      r0, #2
	STRB     r0, [r1, #0x11]
	ADD      r2, #8
	LSL      r0, r2, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	SUB      r0, #0xff
	SUB      r0, #1
	BNE      |loc_08035270|
	STRH     r4, [r1, #0x12]
|loc_08035270|
	POP      {r4, r5}
	BX       lr
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x350]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	MOV      r6, #0xff
	ADD      r6, #0x81
	CMP      r1, #0
	SUB      sp, #0x44
	BNE      |sub_0803528C|
	MOV      r0, #0
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
