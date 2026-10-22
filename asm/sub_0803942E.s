	CODE16
|sub_0803942E|
	LSL      r0, r0, #0
	LDMIA    r7!, {r3, r4, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0x330
	LSR      r7, r6, #1
	LSR      r0, r7, #0x1d
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0]
	BX       lr
|sub_08039440|
|unk_08039440|
	INCBIN	baserom.gba_0x39440_0x39442.extracted
