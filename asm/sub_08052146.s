	CODE16
|sub_08052146|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_0805215E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805215E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r5, #0
	BEQ      |loc_08052180|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052180|
	POP      {r3, r4, r5, pc}
|sub_08052182|
|unk_08052182|
	INCBIN	baserom.gba_0x52182_0x52186.extracted
