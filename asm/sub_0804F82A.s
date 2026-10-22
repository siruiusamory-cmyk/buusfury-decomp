	CODE16
|sub_0804F82A|
	LSR      r1, r6, #1
	PUSH     {r3, lr}
	LDR      r1, [r0, #8]
	LDR      r0, [pc, #8]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x4280
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r6, #0xac
	LSR      r7, r0, #0x20
	LDR      r0, [pc, #0x10]
	MOV      r3, #0x68
	LDR      r0, [r0, #4]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	BX       lr
|sub_0804F854|
|unk_0804F854|
	INCBIN	baserom.gba_0x4f854_0x4f856.extracted
