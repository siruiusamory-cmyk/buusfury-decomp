	CODE16
|sub_0804871A|
	LSR      r4, r0, #0x20
	ADD      r0, #0x24
	LSL      r0, r0, #0xc
	ADR      r6, |sub_08048804|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048732|
|unk_08048732|
	INCBIN	baserom.gba_0x48732_0x48736.extracted
