	CODE16
|sub_08048DEA|
	LSR      r4, r0, #0x20
	ADD      r2, #0xf4
	LSL      r0, r0, #0xc
	ADR      r1, |loc_08048F54|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048DFC|
|unk_08048DFC|
	INCBIN	baserom.gba_0x48dfc_0x48dfe.extracted
