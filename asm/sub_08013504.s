	CODE16
|sub_08013504|
	PUSH     {r4, r5}
	LDRB     r2, [r0, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [pc, #0x104]
	LSL      r2, r2, #3
	ADD      r2, r2, r3
	LDRB     r4, [r2]
	LSL      r3, r1, #0x10
	LSR      r3, r3, #0x10
	LSL      r2, r4, #0x1e
	LSR      r5, r2, #0x1f
	MOV      r2, #0
	CMP      r5, #0
	BEQ      |loc_08013548|
	LDRH     r4, [r0, #0x20]
	CMP      r4, r1
	BGE      |sub_08013536|
	ADD      r1, r2, #0
|loc_0801352A|
	STRH     r1, [r0, #0x20]
	LDRH     r2, [r0, #0x20]
	CMP      r2, r1
	BNE      |loc_0801352A|
	POP      {r4, r5}
	BX       lr
