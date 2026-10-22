	CODE16
|sub_08039BB4|
	MOV      r0, #0
	SUB      r0, r7, r0
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08039BCA|
	LDR      r1, [pc, #0x14]
	STR      r1, [r0]
|loc_08039BCA|
	POP      {r3, pc}
|sub_08039BCC|
|unk_08039BCC|
	INCBIN	baserom.gba_0x39bcc_0x39bce.extracted
