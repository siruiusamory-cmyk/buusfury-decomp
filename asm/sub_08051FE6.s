	CODE16
|sub_08051FE6|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051FF6|
	BL       |GBARam_Free|
|loc_08051FF6|
	POP      {r3, pc}
|sub_08051FF8|
|unk_08051FF8|
	INCBIN	baserom.gba_0x51ff8_0x51ffa.extracted
