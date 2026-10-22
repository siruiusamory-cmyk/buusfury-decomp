	CODE16
|Math_Divide7|
	LSR      r5, r0, #0x20
	MOV      r2, #0xa3
	LSL      r2, r2, #2
	ADD      r2, r0, r2
	PUSH     {r3, lr}
	LDR      r2, [r2]
	ASR      r2, r2, #0xa
	MUL      r1, r2
	MOV      r2, #1
	LSL      r2, r2, #9
	ADD      r0, r0, r2
	LDR      r0, [r0, #0x24]
	LDR      r0, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0xd40
	POP      {r3, pc}
	LSL      r0, r0, #0
	ADD      r0, r1, #0
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, #0x16
	MOV      r3, #2
	LDRSH    r1, [r0, r3]
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	MUL      r0, r4
	SWI      6
	POP      {r4, pc}
	MOV      r1, #1
	LSL      r1, r1, #9
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x24]
	LDR      r0, [r0, #4]
	BX       lr
|sub_0804F8C4|
|unk_0804F8C4|
		MOV r0, #0
		BX       lr
