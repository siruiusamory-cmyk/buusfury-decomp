	CODE16
|sub_0804879E|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r5, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BCC      |loc_08048868|
	LSR      r4, r0, #0x20
	ADD      r0, #0x68
	LSL      r0, r0, #0xc
	POP      {r5, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080487C8|
|unk_080487C8|
	INCBIN	baserom.gba_0x487c8_0x487ca.extracted
