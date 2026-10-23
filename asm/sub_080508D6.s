	CODE16
|sub_080508D6|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	STR      r2, [sp, #0xe0]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080508F2|
	BL       |GBARam_Free|
|loc_080508F2|
	POP      {r3, pc}
|sub_080508F4|
|unk_080508F4|
	INCBIN	baserom.gba_0x508f4_0x508f6.extracted
|sub_080508F6|
	DCW      0x0804
	DCW      0x4a03
