	CODE16
|sub_08051486|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051496|
	BL       |GBARam_Free|
|loc_08051496|
	POP      {r3, pc}
|sub_08051498|
|unk_08051498|
	INCBIN	baserom.gba_0x51498_0x5149a.extracted
