	CODE16
|sub_0804A1FC|
	STRH     r5, [r1, #0x26]
|unk_0804A1FE|
	INCBIN	baserom.gba_0x4a1fe_0x4a202.extracted
	LSL      r0, r0, #0
	STRH     r1, [r0, r6]
	LSL      r0, r0, #0
	LDRSB    r1, [r6, r5]
	LSL      r0, r0, #0
	ADR      r4, |loc_0804A244|
	DCW      0xfffd,0xa43d,0xfffd,0x4311
	LSL      r0, r0, #0
|unk_0804A218|
	INCBIN	baserom.gba_0x4a218_0x4a21a.extracted
	LSL      r0, r0, #0
	LDRB     r1, [r3, r2]
	LSL      r0, r0, #0
	STRH     r5, [r3, r6]
	LSL      r0, r0, #0
	LDRH     r5, [r4, r2]
	LSL      r0, r0, #0
	LDRH     r5, [r7, r0]
	LSL      r0, r0, #0
	LDR      r3, [pc, #0xc4]
	LSL      r0, r0, #0
	LDRSB    r1, [r0, r7]
	LSL      r0, r0, #0
	LDR      r5, [r7, r1]
	LSL      r0, r0, #0
	LDR      r5, [r4, #0x6c]
	LSL      r0, r0, #0
	LDRSB    r5, [r0, r3]
	LSL      r0, r0, #0
	LDMIA    r2!, {r0, r2, r4, r5, r6}
|unk_0804A242|
	INCBIN	baserom.gba_0x4a242_0x4a244.extracted
|loc_0804A244|
|unk_0804A244|
	INCBIN	baserom.gba_0x4a244_0x4a246.extracted
	LSL      r0, r0, #0
	POP      {r0, r2, r3, r4, r7, pc}
|sub_0804A24A|
; cited by 0x0804A22C (a pc-relative load targets 0x0804A2F4)
	INCLUDE rawlabeled_4a24a.s
