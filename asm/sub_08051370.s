	CODE16
|sub_08051370|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805137E|
	BL       |GBARam_Free|
|loc_0805137E|
	POP      {r3, pc}
|sub_08051380|
|unk_08051380|
	INCBIN	baserom.gba_0x51380_0x51382.extracted
|sub_08051382|
	DCW      0x0804
