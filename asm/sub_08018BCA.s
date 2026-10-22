	CODE16
|sub_08018BCA|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08018BDE|
	LDR      r1, [pc, #0x10]
	STR      r1, [r0]
	STR      r4, [r0, #0xc]
|loc_08018BDE|
	POP      {r4, pc}
|sub_08018BE0|
|unk_08018BE0|
	INCBIN	baserom.gba_0x18be0_0x18be2.extracted
