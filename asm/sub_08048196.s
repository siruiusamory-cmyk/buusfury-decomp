	CODE16
|sub_08048196|
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	LDR      r0, [pc, #8]
	BL       |inc_0x0158_0x143f2| + 0x46e0
	POP      {r3, pc}
	LSL      r0, r0, #0
	ASR      r0, r5, #1
	LSL      r0, r0, #0xc
	LDR      r2, [pc, #0x28]
	LDR      r0, [pc, #0x2c]
	MOV      r1, #0x40
	STR      r0, [r2]
	STRB     r1, [r2, #4]
	ADD      r2, #8
	STR      r0, [r2]
	MOV      r1, #0x80
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0x18]
	ADD      r2, #8
	ADD      r1, #0x10
	STR      r0, [r1]
	MOV      r1, #0x20
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0xc]
	ADD      r1, #0x18
	STR      r0, [r1]
	MOV      r0, #0x10
	STRB     r0, [r1, #4]
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, r3, r4
	LSL      r0, r0, #0xc
	ADD      r4, sp, #0x3d0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080481E4|
|unk_080481E4|
	INCBIN	baserom.gba_0x481e4_0x481e6.extracted
