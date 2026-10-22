	CODE16
|sub_08051FBE|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051FCE|
	BL       |GBARam_Free|
|loc_08051FCE|
	POP      {r3, pc}
|sub_08051FD0|
|unk_08051FD0|
	INCBIN	baserom.gba_0x51fd0_0x51fd2.extracted
