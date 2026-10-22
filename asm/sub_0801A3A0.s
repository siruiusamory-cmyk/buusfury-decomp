	CODE16
|sub_0801A3A0|
|unk_0801A3A0|
		LDRB r1, [r0, #0x15]
		LSL r1, r1, #1
		ADD r1, r1, r0
		ADD r1, #0x2e
		LDRB r1, [r1]
		LDR r2, [pc, #0x1f0]
		ADD r2, #0xf
		LDRB r1, [r2, r1]
	INCBIN  baserom.gba_0x1a3b0_0x1a3b2.extracted
|sub_0801A3B2|
|unk_0801A3B2|
	INCBIN	baserom.gba_0x1a3b2_0x1a3b6.extracted
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	LDRB     r1, [r0, #0x15]
	LSL      r1, r1, #1
	ADD      r0, r1, r0
	ADD      r0, #0x2e
	LDRB     r5, [r0]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801A3D8|
	LDR      r1, [pc, #0x1d4]
	STR      r1, [r0]
	STR      r5, [r0, #0xc]
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_0801A3D8|
	ADD      r5, r0, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
|sub_0801A3EC|
|unk_0801A3EC|
	INCBIN	baserom.gba_0x1a3ec_0x1a3f2.extracted
