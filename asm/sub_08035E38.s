	CODE16
|sub_08035E38|
	ADD      r2, #0x68
	LSL      r0, r0, #0xc
	LDR      r0, [r1, #0x58]
	ADD      r0, #0x4c
	LDR      r0, [r0, #0x54]
	LDR      r2, [r1, #0x50]
	CMP      r0, r2
	BNE      |loc_08035E54|
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	MOV      r0, #6
	STRB     r0, [r1, #0x11]
|loc_08035E54|
	BX       lr
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDRH     r1, [r1, #0x12]
	ADD      r1, #1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r0, #0x12]
	LDR      r2, [r0, #0x50]
	LSR      r1, r1, #2
	LDR      r2, [r2]
	ADD      r1, #6
	CMP      r2, r1
	BGT      |sub_08035E7E|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
