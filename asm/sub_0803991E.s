	CODE16
|sub_0803991E|
	MOV      r2, sp
	LDR      r2, [r2]
	STRH     r2, [r0, #0x16]
	MOV      r2, #0xff
	ADD      r2, #0xf1
	LDRH     r3, [r0, #0x16]
	LDR      r2, [r2, r1]
	MOV      r4, #0xff
	ADD      r4, #0x77
	STRH     r3, [r4, r2]
	ADD      r2, #0xff
	ADD      r2, #0xc1
	LDRH     r3, [r0, #0x16]
	LDR      r2, [r2, #0x38]
	STRH     r3, [r4, r2]
	ADD      r2, #0xff
	ADD      r2, #0xc1
	LDR      r2, [r2, #0x38]
	LDRH     r0, [r0, #0x16]
	ADD      r2, #0xff
	ADD      r2, #0x61
	STRH     r0, [r2, #0x16]
	LDRH     r0, [r1, #0x12]
	ADD      r0, #1
	STRH     r0, [r1, #0x12]
	ADD      sp, #8
	POP      {r4}
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	MOV      r6, #1
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08039976|
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	STR      r6, [r5, #4]
|loc_08039976|
	LDRH     r1, [r4, #0x12]
	ADD      r0, r6, #0
	CMP      r1, #0x80
	BHI      |loc_08039980|
	MOV      r0, #0
|loc_08039980|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08039992|
	LDR      r1, [pc, #8]
	STR      r1, [r0]
|loc_08039992|
	POP      {r3, pc}
|sub_08039994|
|unk_08039994|
	INCBIN	baserom.gba_0x39994_0x39996.extracted
	CODE16
|dat_08039996|
	DCW      0x0300
|unk_08039998|
	INCBIN	baserom.gba_0x39998_0x3999a.extracted
|dat_0803999A|
	DCW      0x0804
	DCW      0x1c08
	DCW      0x30ff
	DCW      0x30c1
