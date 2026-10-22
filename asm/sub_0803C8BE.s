	CODE16
|sub_0803C8BE|
	PUSH     {r3, lr}
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803C8CE|
	LDR      r1, [pc, #0x10]
	STR      r1, [r0]
|loc_0803C8CE|
	POP      {r3, pc}
|sub_0803C8D0|
|unk_0803C8D0|
	INCBIN	baserom.gba_0x3c8d0_0x3c8d2.extracted
