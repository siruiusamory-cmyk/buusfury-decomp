	CODE16
|sub_0800051A|
	LDR      r1, [pc, #0x14c]
	PUSH     {r4}
	LDR      r1, [r1, #0x14]
	MOV      r3, #0x68
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	CMP      r0, #0
	BGE      |loc_08000534|
	MOV      r0, #0
|loc_08000534|
	ADD      r2, r1, #0
	ADD      r2, #0x1c
	MOV      r3, #0
	LDRSH    r4, [r2, r3]
	CMP      r4, r0
	BGE      |loc_08000542|
	LDRSH    r0, [r2, r3]
|loc_08000542|
	LDRB     r2, [r1, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [pc, #0x120]
	LSL      r2, r2, #3
	ADD      r2, r2, r3
	LDRB     r2, [r2]
	LSL      r3, r2, #0x1e
	LSR      r3, r3, #0x1f
	BEQ      |sub_08000568|
	ADD      r1, #0x20
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
|loc_0800055C|
	STRH     r0, [r1]
	LDRH     r2, [r1]
	CMP      r2, r0
	BNE      |loc_0800055C|
	POP      {r4}
	BX       lr
