	CODE16
|sub_08048736|
	LSR      r4, r0, #0x20
	ADD      r0, #0x30
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08048860|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r2!, {r5, r6}
	LSR      r4, r0, #0x20
	ADD      r0, #0x3c
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0xb0
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #8
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r2!, {r3, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r0, #0x4c
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x130
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BCC      |loc_08048884|
	LSR      r4, r0, #0x20
	ADD      r0, #0x5c
	LSL      r0, r0, #0xc
	POP      {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804879C|
|unk_0804879C|
	INCBIN	baserom.gba_0x4879c_0x4879e.extracted
