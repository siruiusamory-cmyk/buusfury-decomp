	CODE16
|sub_080481E6|
	LSL      r0, r0, #0xc
	LDR      r3, [sp, #0x390]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0x28]
	LDR      r0, [pc, #0x2c]
	MOV      r1, #1
	STR      r0, [r2]
	STRB     r1, [r2, #4]
	ADD      r2, #8
	STR      r0, [r2]
	MOV      r1, #0
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0x18]
	ADD      r2, #8
	ADD      r1, #0x10
	STR      r0, [r1]
	MOV      r1, #2
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0xc]
	ADD      r1, #0x18
	STR      r0, [r1]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	BX       lr
	LSL      r0, r0, #0
	ADD      r4, r7, r4
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r3, r5}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048228|
|unk_08048228|
	INCBIN	baserom.gba_0x48228_0x4822a.extracted
