	CODE16
|sub_08052798|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080527A6|
	BL       |GBARam_Free|
|loc_080527A6|
	POP      {r3, pc}
|sub_080527A8|
|unk_080527A8|
	INCBIN	baserom.gba_0x527a8_0x527aa.extracted
|sub_080527AA|
	DCW      0x0804
