	CODE16
|sub_08050704|
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
|unk_0805070C|
	INCBIN	baserom.gba_0x5070c_0x5070e.extracted
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0805072C|
	LDR      r0, [pc, #0x28]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0805072C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
