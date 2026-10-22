	CODE16
|sub_080487CA|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_080487D4|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r5!, {r3, r4}
	LSR      r4, r0, #0x20
	ADD      r0, #0x74
	LSL      r0, r0, #0xc
|unk_080487E8|
	INCBIN	baserom.gba_0x487e8_0x487ea.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080487F4|
|unk_080487F4|
	INCBIN	baserom.gba_0x487f4_0x487f6.extracted
