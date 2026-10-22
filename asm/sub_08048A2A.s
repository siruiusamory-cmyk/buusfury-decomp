	CODE16
|sub_08048A2A|
	LSL      r0, r0, #0xc
|loc_08048A2C|
	LDR      r3, [sp, #0x3e0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048A38|
|unk_08048A38|
	INCBIN	baserom.gba_0x48a38_0x48a3a.extracted
