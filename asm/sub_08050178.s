	CODE16
|sub_08050178|
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r2, [r0]
	LDR      r3, [r2, #4]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_08050196|
	MOV      r0, #0
|loc_08050196|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r1, #0x30
	LSL      r0, r0, #0xc
	ADD      r0, r1, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	LDR      r1, [r0, #0x24]
	ADD      r1, #1
	STR      r1, [r0, #0x24]
	MOV      r0, #1
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x11
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed58
	CMP      r0, #0
	BNE      |sub_080501D0|
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed58
	CMP      r0, #0
	BNE      |sub_080501D0|
	MOV      r0, #1
	POP      {r4, pc}
