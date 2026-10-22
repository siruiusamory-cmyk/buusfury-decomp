	CODE16
|sub_0803BEB2|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_0803BEC8|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x54]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0803BEC8|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803BEE2|
	LDR      r1, [pc, #0x40]
	STR      r1, [r0]
|loc_0803BEE2|
	ADD      r5, r0, #0
	MOV      r1, #0x10
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
|sub_0803BEF6|
|unk_0803BEF6|
		LDR r0, [r1, #0x58]
		ADD r0, #0x40
		LDR r0, [r0, #0x54]
		LDR r1, [r1, #0x50]
		CMP r0, r1
		BNE      |sub_0803BF06|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x6d48
