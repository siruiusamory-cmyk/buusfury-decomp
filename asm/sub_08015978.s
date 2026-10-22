	CODE16
|sub_08015978|
	PUSH     {r4, lr}
	LDR      r4, [r1, #4]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801598E|
	LDR      r1, [pc, #0x10]
	STR      r1, [r0]
	MOV      r1, #0xc
	STRB     r1, [r0, #4]
|loc_0801598E|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xec28
	POP      {r4, pc}
|sub_08015998|
|unk_08015998|
	INCBIN	baserom.gba_0x15998_0x1599a.extracted
