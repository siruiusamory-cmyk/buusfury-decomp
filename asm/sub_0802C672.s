	CODE16
|sub_0802C672|
	PUSH     {r3, lr}
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802C682|
	LDR      r1, [pc, #0x18]
	STR      r1, [r0]
|loc_0802C682|
	POP      {r3, pc}
|sub_0802C684|
|unk_0802C684|
	INCBIN	baserom.gba_0x2c684_0x2c686.extracted
