	CODE16
|sub_0803930A|
	MOV      r2, #0xff
	ADD      r2, #0xf9
	LDR      r2, [r2, r0]
	CMP      r2, #0
	BEQ      |loc_08039324|
|loc_08039314|
	ADD      r0, #0xff
	ADD      r0, #0xc1
	LDR      r0, [r0, #0x38]
	MOV      r2, #0xff
	ADD      r2, #0xf9
	LDR      r2, [r2, r0]
	CMP      r2, #0
	BNE      |loc_08039314|
|loc_08039324|
	MOV      r2, #0xff
	ADD      r2, #0xf9
	STR      r5, [r2, r0]
	STR      r0, [r1, #0x3c]
	LDRH     r0, [r4, #0x12]
	CMP      r0, #0x48
	BCC      |loc_08039340|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08039340|
	LDRH     r0, [r4, #0x12]
	ADD      r0, #1
	STRH     r0, [r4, #0x12]
	ADD      sp, #0x30
	POP      {r4, r5, r6, pc}
|sub_0803934A|
|unk_0803934A|
	INCBIN	baserom.gba_0x3934a_0x3934e.extracted
