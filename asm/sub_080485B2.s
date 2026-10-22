	CODE16
|sub_080485B2|
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x20
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r6!, {r2, r3, r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	CMP      r7, #0xa8
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0x160
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080485DC|
|unk_080485DC|
	INCBIN	baserom.gba_0x485dc_0x485de.extracted
