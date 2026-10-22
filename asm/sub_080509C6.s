	CODE16
|sub_080509C6|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	STR      r3, [sp, #0x390]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080509E2|
	BL       |GBARam_Free|
|loc_080509E2|
	POP      {r3, pc}
|sub_080509E4|
|unk_080509E4|
	INCBIN	baserom.gba_0x509e4_0x509e6.extracted
