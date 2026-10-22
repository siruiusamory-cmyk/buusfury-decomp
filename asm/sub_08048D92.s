	CODE16
|sub_08048D92|
	LSL      r0, r0, #0xc
	STMIA    r6!, {r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048DA0|
	DCW      0x32d8
	DCW      0x0300,0xde24
|loc_08048DA6|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048DB0|
|unk_08048DB0|
	INCBIN	baserom.gba_0x48db0_0x48db2.extracted
