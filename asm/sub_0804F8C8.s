	CODE16
|sub_0804F8C8|
	LDR      r0, [pc, #4]
	LDR      r0, [r0]
	BX       lr
	LSL      r0, r0, #0
	MOV      r7, #0x20
	LSR      r7, r0, #0x20
	LDR      r0, [pc, #4]
	LDR      r0, [r0, #0x1c]
	BX       lr
	LSL      r0, r0, #0
	ASR      r0, r4, #0x1a
	LSR      r7, r0, #0x20
	LDR      r0, [pc, #4]
	LDR      r0, [r0, #0x18]
	BX       lr
	LSL      r0, r0, #0
	ASR      r0, r4, #0x1a
	LSR      r7, r0, #0x20
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2, #8]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r0, #0
	BX       lr
	PUSH     {r4}
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	LDR      r3, [r1]
	LDR      r4, [r1, #8]
	LDR      r1, [r1, #4]
	ADD      r0, #8
	LDR      r0, [r0, #4]
	ADD      r3, r3, r4
	ADD      r0, r1, r0
	SUB      sp, #8
	ASR      r1, r3, #1
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	STR      r3, [sp]
	STR      r1, [sp]
	STR      r0, [sp, #4]
	STR      r0, [r2, #4]
	STR      r1, [r2]
	ADD      sp, #8
	POP      {r4}
	BX       lr
|sub_0804F92C|
|unk_0804F92C|
		MOV r0, #0
		BX       lr
		MOV r0, #4
		BX       lr
		MOV r0, #0
		BX       lr
		MOV r0, #4
		BX       lr
		MOV r0, #4
		BX       lr
		MOV r0, #0xff
		BX       lr
