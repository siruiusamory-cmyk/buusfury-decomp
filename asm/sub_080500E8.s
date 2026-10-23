	CODE16
|sub_080500E8|
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r2, [r0]
	LDR      r3, [r2, #4]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LDRB     r1, [r1, #0x11]
	MOV      r0, #1
	CMP      r1, #3
	BEQ      |loc_08050102|
	MOV      r0, #0
|loc_08050102|
	BX       lr
	LDRB     r1, [r1, #0x11]
	MOV      r0, #1
	CMP      r1, #3
	BEQ      |loc_0805010E|
	MOV      r0, #0
|loc_0805010E|
	BX       lr
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0805011E|
	MOV      r0, #0
|loc_0805011E|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	SUB      r0, r7, r4
	LSL      r0, r0, #0xc
	MOV      r0, #1
	BX       lr
|sub_0805012C|
|unk_0805012C|
		BX       lr
