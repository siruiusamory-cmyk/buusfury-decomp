	CODE16
|sub_08006E0A|
	PUSH     {r3, lr}
	BL       |loc_08007064|
	POP      {r3, pc}
	LSL      r0, r0, #0
	STR      r6, [sp, #0x330]
	LSR      r4, r0, #0x20
|unk_08006E18|
	INCBIN	baserom.gba_0x6e18_0x6e1a.extracted
|dat_08006E1A|
	DCW      0x0804
	DCW      0x95b4
	DCW      0x0804