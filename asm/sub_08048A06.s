	CODE16
|sub_08048A06|
	LSR      r4, r0, #0x20
	ADD      r1, #0x30
	LSL      r0, r0, #0xc
	LDMIA    r7!, {r2, r3, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048A18|
|unk_08048A18|
	INCBIN	baserom.gba_0x48a18_0x48a1a.extracted
