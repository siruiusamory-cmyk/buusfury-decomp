	CODE16
|sub_0804EC22|
	LSL      r0, r0, #0
	MOV      r1, #0
	STR      r1, [r0, #8]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	MOV      r2, #3
	LSL      r2, r2, #0xf
	ADD      r4, r0, #0
	MOV      r1, #0
	LSL      r0, r2, #0xa
	BL       |sub_0804912C|
	LDR      r1, [pc, #0x14]
	MOV      r0, #0
	STRB     r0, [r1]
	STRB     r0, [r1, #1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #0x12
	STRH     r0, [r1, #0x10]
	ADD      r0, r4, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0x935a
	POP      {r4, pc}
	LSL      r0, r0, #0
	LSL      r2, r2, #1
	LSL      r0, r0, #0x10
	SUB      r7, #0x5f
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	MOV      r2, #3
	LSL      r2, r2, #0xf
	ADD      r4, r0, #0
	MOV      r1, #0
	LSL      r0, r2, #0xa
	BL       |sub_0804912C|
	LDR      r1, [pc, #0x14]
	MOV      r0, #0
	STRB     r0, [r1]
	STRB     r0, [r1, #1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #0x12
	STRH     r0, [r1, #0x10]
	ADD      r0, r4, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0x9e20
	POP      {r4, pc}
	LSL      r0, r0, #0
	LSL      r2, r2, #1
	LSL      r0, r0, #0x10
	SUB      r7, #0x5f
	LSL      r0, r0, #0
	MOV      r2, #0x47
	LSL      r2, r2, #3
	PUSH     {r3, lr}
	ADD      r0, r0, r2
	BL       |inc_0x0158_0x143f2| + 0xa944
	POP      {r3, pc}
|sub_0804EC9A|
|unk_0804EC9A|
	INCBIN  baserom.gba_0x4ec9a_0x4ec9c.extracted
		BX       lr
|sub_0804EC9E|
	DCW      0x0000
	DCW      0x2245
	DCW      0x00d2
