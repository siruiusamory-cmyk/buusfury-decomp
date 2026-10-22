	CODE16
|sub_08050F72|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050F82|
	BL       |GBARam_Free|
|loc_08050F82|
	POP      {r3, pc}
|sub_08050F84|
|unk_08050F84|
	INCBIN	baserom.gba_0x50f84_0x50f86.extracted
