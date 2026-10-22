	CODE16
|sub_08051BDE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4, #8]
	LDR      r0, [pc, #0x24]
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	CMP      r0, #0
	BEQ      |loc_08051C00|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08051C00|
	CMP      r5, #0
	BEQ      |loc_08051C0A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051C0A|
	POP      {r3, r4, r5, pc}
|sub_08051C0C|
|unk_08051C0C|
	INCBIN	baserom.gba_0x51c0c_0x51c0e.extracted
