	CODE16
|sub_08048A1A|
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08048B80|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048A28|
|unk_08048A28|
	INCBIN	baserom.gba_0x48a28_0x48a2a.extracted
