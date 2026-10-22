	CODE16
|sub_0805107E|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	STR      r1, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805109A|
	BL       |GBARam_Free|
|loc_0805109A|
	POP      {r3, pc}
|sub_0805109C|
|unk_0805109C|
	INCBIN	baserom.gba_0x5109c_0x5109e.extracted
