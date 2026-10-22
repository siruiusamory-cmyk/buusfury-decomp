	CODE16
|sub_08007A40|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08007A54|
	LDR      r1, [pc, #0xc]
	STRB     r4, [r0, #4]
	STR      r1, [r0]
|loc_08007A54|
	POP      {r4, pc}
|sub_08007A56|
|unk_08007A56|
	INCBIN	baserom.gba_0x7a56_0x7a5a.extracted
