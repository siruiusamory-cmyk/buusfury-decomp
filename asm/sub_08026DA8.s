	CODE16
|sub_08026DA8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x28]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [pc, #0x28]
	LDRH     r1, [r4, #0x14]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	LDR      r0, [pc, #0x20]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08026DCA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08026DCA|
	POP      {r3, r4, r5, pc}
|sub_08026DCC|
	DCW      0xda60
	DCW      0x0804,0x802c,0x0000,0xffff,0xfe00,0xe148,0x0804,0xcf24
	DCW      0x0874,0xe454
|sub_08026DE2|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r6, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08026DFE|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08026DFE|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
