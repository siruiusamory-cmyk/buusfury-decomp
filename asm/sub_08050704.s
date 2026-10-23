	CODE16
|sub_08050704|
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
|unk_0805070C|
	INCBIN	baserom.gba_0x5070c_0x5070e.extracted
|dat_0805070E|
	DCW      0x0804
	DCW      0x0000
	DCW      0x0601