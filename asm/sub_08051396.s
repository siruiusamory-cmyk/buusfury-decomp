	CODE16
|sub_08051396|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [sp, #0x130]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080513B2|
	BL       |GBARam_Free|
|loc_080513B2|
	POP      {r3, pc}
|sub_080513B4|
|unk_080513B4|
	INCBIN	baserom.gba_0x513b4_0x513b6.extracted
|sub_080513B6|
	DCW      0x0804
