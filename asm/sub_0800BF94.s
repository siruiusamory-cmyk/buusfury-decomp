	CODE16
|sub_0800BF94|
	PUSH     {r4, lr}
	LDRB     r1, [r0, #0x10]
	ADD      r1, #0xff
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	STRB     r1, [r0, #0x10]
	BNE      |sub_0800BFCA|
	LDR      r4, [pc, #0x104]
	ADD      r1, r0, #0
	SUB      r4, #0xc
	LDR      r0, [r4]
	BL       |loc_08011944|
	LDR      r0, [r4, #4]
	ADD      r0, #0x80
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |loc_0800BFC6|
	MOV      r0, #0
	BL       |Object_Construct5|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |List_Append|
|loc_0800BFC6|
	MOV      r0, #0
	POP      {r4, pc}
