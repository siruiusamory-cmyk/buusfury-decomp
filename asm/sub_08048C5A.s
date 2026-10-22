	CODE16
|sub_08048C5A|
	LSL      r0, r0, #0xc
	LDMIA    r7!, {r3, r5, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
|loc_08048C70|
	STMIA    r6!, {r3, r4, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r2, #0x78
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0xa0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048C84|
|unk_08048C84|
	INCBIN	baserom.gba_0x48c84_0x48c86.extracted
