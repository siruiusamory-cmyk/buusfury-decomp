	CODE16
|sub_0802172A|
	LSR      r2, r6, #1
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
|unk_08021730|
	INCBIN	baserom.gba_0x21730_0x21732.extracted
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LDMIA    r2!, {r7}
	LSR      r4, r0, #0x20
|unk_0802173C|
	INCBIN	baserom.gba_0x2173c_0x2173e.extracted
|dat_0802173E|
	DCW      0x0804