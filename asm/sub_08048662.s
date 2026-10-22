	CODE16
|sub_08048662|
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08048928|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [sp, #0x170]
	LSR      r4, r0, #0x20
	CMP      r7, #0xf0
	LSL      r0, r0, #0xc
	POP      {pc}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804868C|
|unk_0804868C|
	INCBIN	baserom.gba_0x4868c_0x4868e.extracted
