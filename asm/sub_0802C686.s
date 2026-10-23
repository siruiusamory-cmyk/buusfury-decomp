	CODE16
|sub_0802C686|
	LSL      r0, r0, #0xc
	ADD      r0, #0x94
	LSL      r0, r0, #0xc
	BL       |loc_0802d674| + 0x1a
	SUB      r0, r0, r4
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #0x150]
	LSR      r5, r6, #1
|unk_0802C698|
	INCBIN	baserom.gba_0x2c698_0x2c69a.extracted
|dat_0802C69A|
	DCW      0x0804