	CODE16
|sub_08050C4E|
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
	BEQ      |loc_08050C6A|
	BL       |GBARam_Free|
|loc_08050C6A|
	POP      {r3, pc}
|sub_08050C6C|
|unk_08050C6C|
	INCBIN	baserom.gba_0x50c6c_0x50c6e.extracted
|sub_08050C6E|
	DCW      0x0804
