	CODE16
|sub_0805285E|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805286E|
	BL       |GBARam_Free|
|loc_0805286E|
	POP      {r3, pc}
|sub_08052870|
|unk_08052870|
	INCBIN	baserom.gba_0x52870_0x52872.extracted
