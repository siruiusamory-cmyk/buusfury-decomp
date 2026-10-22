	CODE16
|sub_08050034|
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_08050042|
	MOV      r0, #0
|loc_08050042|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r2, #0x14
	LSL      r0, r0, #0xc
	LDR      r1, [r1, #0x14]
	LDR      r2, [pc, #0xc]
	MOV      r0, #1
	CMP      r1, r2
	BEQ      |loc_08050058|
	MOV      r0, #0
|loc_08050058|
	BX       lr
	LSL      r0, r0, #0
	SUB      r0, r6, r4
	LSL      r0, r0, #0xc
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0805006E|
	MOV      r0, #0
|loc_0805006E|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r2, #0xa0
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	BL       |inc_0x0158_0x143f2| + 0xed46
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r0, #1
	BX       lr
	LDR      r0, [r1, #0x58]
	ADD      r0, #0x4c
	LDR      r0, [r0, #0x54]
	LDR      r2, [r1, #0x50]
	CMP      r0, r2
	BNE      |loc_0805009A|
	LDRH     r0, [r1, #0x12]
	CMP      r0, #0xf8
	BCC      |sub_0805009E|
|loc_0805009A|
	MOV      r0, #1
	BX       lr
