	CODE16
|sub_080488F6|
	LSL      r0, r0, #0xc
	BCS      |sub_0804888C|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_08048900|
	STR      r0, [r1]
	BX       lr
|sub_08048904|
|unk_08048904|
	INCBIN	baserom.gba_0x48904_0x48906.extracted
