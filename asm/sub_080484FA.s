	CODE16
|sub_080484FA|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x50
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048508|
|unk_08048508|
	INCBIN	baserom.gba_0x48508_0x4850a.extracted
