	CODE16
|sub_08048C46|
	LSR      r4, r0, #0x20
	ADD      r2, #0x6c
	LSL      r0, r0, #0xc
	ADR      r0, |loc_08049010|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048C58|
|unk_08048C58|
	INCBIN	baserom.gba_0x48c58_0x48c5a.extracted
