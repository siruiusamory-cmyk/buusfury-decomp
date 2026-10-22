	CODE16
|sub_08048DC2|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048DD0|
|unk_08048DD0|
	INCBIN	baserom.gba_0x48dd0_0x48dd2.extracted
