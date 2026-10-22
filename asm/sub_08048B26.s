	CODE16
|sub_08048B26|
	LSL      r0, r0, #0xc
	STMIA    r6!, {r5, r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_08048B30|
	STR      r0, [r1]
	BX       lr
|sub_08048B34|
|unk_08048B34|
	INCBIN	baserom.gba_0x48b34_0x48b36.extracted
