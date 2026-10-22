	CODE16
|sub_08052E46|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0x934a
	CMP      r5, #0
	BEQ      |loc_08052E5E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052E5E|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052E6E|
	BL       |GBARam_Free|
|loc_08052E6E|
	POP      {r3, pc}
|sub_08052E70|
|unk_08052E70|
	INCBIN	baserom.gba_0x52e70_0x52e72.extracted
