	CODE16
|loc_080001C6|
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x1fc]
	CMP      r0, #0
	BGE      |loc_080001DC|
	ADD      r0, #1
|unk_080001D0|
	INCBIN	baserom.gba_0x1d0_0x1d2.extracted
	LDR      r0, [r4, #0x18]
	MOV      r1, #7
	BL       |List_CallMethod1|
	POP      {r4, pc}
|loc_080001DC|
	CMP      r0, #0
	BNE      |loc_080001EC|
	LDR      r1, [pc, #0x1e8]
	LDR      r1, [r1]
	CMP      r1, #0
	BEQ      |loc_080001F6|
	ADD      r0, r1, #0
	POP      {r4, pc}
|loc_080001EC|
	CMP      r0, #9
	BNE      |loc_080001F6|
	LDR      r0, [pc, #0x1dc]
	LDR      r0, [r0]
	POP      {r4, pc}
|loc_080001F6|
	BL       |sub_08000158|
	ADD      r2, r0, #0
	LDR      r0, [r4, #0x18]
	MOV      r1, #5
	BL       |List_CallMethod1|
	POP      {r4, pc}
	LDR      r1, [pc, #0x1cc]
	LDR      r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x1b8]
	STR      r0, [r1]
	BX       lr
	LDR      r1, [pc, #0x1b4]
	LDR      r2, [r1, #4]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x1a0]
	STR      r0, [r1, #4]
	BX       lr
	LDR      r1, [pc, #0x19c]
	LDR      r2, [r1, #8]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x188]
	STR      r0, [r1, #8]
	BX       lr
	LDR      r1, [pc, #0x184]
	LDR      r2, [r1, #0xc]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x170]
	STR      r0, [r1, #0xc]
	BX       lr
	LDR      r1, [pc, #0x170]
	LDR      r1, [r1]
	STR      r0, [r1]
	BX       lr
	LDR      r1, [pc, #0x168]
	LDR      r1, [r1]
	LDR      r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x154]
	LDR      r1, [r1]
	STR      r0, [r1, #4]
	BX       lr
	LDR      r1, [pc, #0x14c]
	LDR      r1, [r1]
	LDR      r2, [r1, #4]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x138]
	LDR      r1, [r1]
	STR      r0, [r1, #8]
	BX       lr
	LDR      r1, [pc, #0x130]
	LDR      r1, [r1]
	LDR      r2, [r1, #8]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x11c]
	LDR      r1, [r1]
	STR      r0, [r1, #0xc]
	BX       lr
	LDR      r1, [pc, #0x114]
	LDR      r1, [r1]
	LDR      r2, [r1, #0xc]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x104]
	STR      r0, [r1]
	BX       lr
	LDR      r1, [pc, #0xfc]
	LDR      r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0xec]
	STR      r0, [r1, #4]
	BX       lr
	LDR      r1, [pc, #0xe4]
	LDR      r2, [r1, #4]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0xd4]
	STR      r0, [r1, #8]
	BX       lr
	LDR      r1, [pc, #0xcc]
	LDR      r2, [r1, #8]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0xbc]
	STR      r0, [r1, #0xc]
	BX       lr
	LDR      r1, [pc, #0xb4]
	LDR      r2, [r1, #0xc]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x90]
	MOV      r3, #0x68
	LDR      r1, [r1, #0x14]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	ADD      r1, #0x16
	MOV      r3, #0
	LDRSH    r2, [r1, r3]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x68]
	MOV      r3, #0x68
	LDR      r1, [r1, #0x14]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	ADD      r1, #0x18
	MOV      r3, #0
	LDRSH    r2, [r1, r3]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x44]
	MOV      r3, #0x68
	LDR      r1, [r1, #0x14]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	ADD      r1, #0x1c
	MOV      r3, #0
	LDRSH    r2, [r1, r3]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x1c]
	LDR      r2, [pc, #0x34]
	LDR      r1, [r1, #0x14]
	ADD      r1, r1, r2
	LDR      r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
|sub_080003C0|
|unk_080003C0|
	INCBIN	baserom.gba_0x3c0_0x3c2.extracted
