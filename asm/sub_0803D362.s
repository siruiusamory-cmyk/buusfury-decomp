	CODE16
|sub_0803D362|
	LSL      r0, r0, #0xc
	STMIA    r5!, {r2, r3}
	LSR      r7, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
|unk_0803D370|
	INCBIN	baserom.gba_0x3d370_0x3d372.extracted
|dat_0803D372|
	DCW      0x0804