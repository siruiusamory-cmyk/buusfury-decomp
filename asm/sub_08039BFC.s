	CODE16
|sub_08039BFC|
	PUSH     {r3, lr}
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08039C0C|
	LDR      r1, [pc, #4]
	STR      r1, [r0]
|loc_08039C0C|
	POP      {r3, pc}
|sub_08039C0E|
|unk_08039C0E|
	INCBIN	baserom.gba_0x39c0e_0x39c12.extracted
