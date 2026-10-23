	CODE16
|sub_0805111A|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	STR      r2, [sp, #0x270]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051136|
	BL       |GBARam_Free|
|loc_08051136|
	POP      {r3, pc}
|sub_08051138|
|unk_08051138|
	INCBIN	baserom.gba_0x51138_0x5113a.extracted
|sub_0805113A|
	DCW      0x0804
