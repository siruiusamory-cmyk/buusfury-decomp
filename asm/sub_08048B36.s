	CODE16
|sub_08048B36|
	LSL      r0, r0, #0xc
	BVS      |loc_08048A94|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048B44|
|unk_08048B44|
	INCBIN	baserom.gba_0x48b44_0x48b46.extracted
