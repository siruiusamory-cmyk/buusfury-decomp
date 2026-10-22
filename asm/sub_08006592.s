	CODE16
|sub_08006592|
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	LSL      r4, r1, #5
	LSR      r7, r0, #0x20
	ADD      r4, r2, r4
	LSL      r0, r0, #0xc
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	STR      r4, [sp, #0x360]
	LSR      r4, r0, #0x20
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
	MOV      r0, #0
	BX       lr
	LDR      r0, [pc, #0x50]
	CMP      r1, #0
	BEQ      |loc_080065D4|
	CMP      r1, #1
	BEQ      |loc_080065DA|
	CMP      r1, #2
	BNE      |sub_080065E0|
	LDR      r0, [r0, #8]
	LDRB     r0, [r0]
	BX       lr
|loc_080065D4|
	LDR      r0, [r0, #8]
	LDRB     r0, [r0, #1]
	BX       lr
|loc_080065DA|
	LDR      r0, [r0, #8]
	LDRB     r0, [r0, #2]
	BX       lr
