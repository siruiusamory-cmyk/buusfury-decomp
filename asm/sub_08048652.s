	CODE16
|sub_08048652|
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x250
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048660|
|unk_08048660|
	INCBIN	baserom.gba_0x48660_0x48662.extracted
