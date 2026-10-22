	CODE16
|sub_08035DCE|
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08036178|
	LSR      r5, r6, #1
	BLS      |loc_08035D7C|
	LSR      r7, r5, #1
	ADD      r2, #0x60
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, lr}
	ADD      r0, r1, #0
	LDRH     r1, [r1, #0x12]
	ADD      r1, #1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r0, #0x12]
	LDR      r2, [r0, #0x50]
	LSR      r1, r1, #3
	LDR      r2, [r2]
	SUB      r3, r2, #1
	CMP      r3, r1
	BEQ      |loc_08035E0C|
	SUB      r2, #2
	CMP      r2, r1
	BNE      |loc_08035E22|
|loc_08035E0C|
	LDRB     r2, [r0, #0x11]
	CMP      r2, r1
	BEQ      |loc_08035E22|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0xa5
	LDR      r4, [r2]
	MOV      r3, #1
	LSL      r3, r3, #0xb
	ADD      r3, r4, r3
	STR      r3, [r2]
|loc_08035E22|
	LDR      r2, [r0, #0x50]
	LDR      r2, [r2]
	CMP      r2, r1
	BGT      |sub_08035E30|
	BL       |inc_0x0158_0x143f2| + 0xed20
	POP      {r4, pc}
