	CODE16
|sub_08052254|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052262|
	BL       |GBARam_Free|
|loc_08052262|
	POP      {r3, pc}
|sub_08052264|
|unk_08052264|
	INCBIN	baserom.gba_0x52264_0x52266.extracted
|sub_08052266|
	DCW      0x0804
