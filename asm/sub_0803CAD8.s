	CODE16
|sub_0803CAD8|
	STRB     r6, [r4, #0x10]
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803CAE8|
	LDR      r1, [pc, #0x54]
	STR      r1, [r0]
|loc_0803CAE8|
	ADD      r5, r0, #0
	MOV      r1, #4
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      sp, #0x38
	POP      {r4, r5, r6, pc}
|sub_0803CAFE|
|unk_0803CAFE|
		LDR r0, [r1, #0x58]
		LDR r0, [r0, #0x64]
		LDR r1, [r1, #0x50]
		CMP r0, r1
		BNE      |sub_0803CB0C|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x794e
