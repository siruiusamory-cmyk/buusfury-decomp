	CODE16
|sub_0803DCE6|
|unk_0803DCE6|
		LDR r2, [r5, #0xc]
		MOV r1, #0x5c
		LDR r2, [r2]
		ADD r0, sp, #4
		LDRH r1, [r2, r1]
		LSL r1, r1, #1
		LDRH r1, [r2, r1]
		ADD r1, #1
		LSL r3, r1, #1
|loc_0803DCF8|
		LDRH r1, [r4]
		LDR r2, [r5, #0xc]
		CMP r1, #0xff
		BLO      |loc_0803DD06|
		LDR r2, [r2, #4]
		ADD r2, #1
		B        |loc_0803DD12|
|loc_0803DD06|
		LDR r2, [r2]
		LSL r7, r1, #1
		LDRH r7, [r2, r7]
		LSL r7, r7, #1
		LDRH r2, [r2, r7]
		ADD r2, #1
|loc_0803DD12|
		ADD r3, r3, r2
		CMP r3, r6
		BGT      |loc_0803DD20|
		ADD r4, #2
		STRH r1, [r0]
		ADD r0, #2
		B        |loc_0803DCF8|
|loc_0803DD20|
		MOV r1, #0x2e
		STRH r1, [r0]
		ADD r0, #2
		STRH r1, [r0]
		ADD r1, r0, #2
		MOV r0, #0
		STRH r0, [r1]
		ADD r1, sp, #4
		ADD r0, r5, #0
	INCBIN  baserom.gba_0x3dd32_0x3dd34.extracted
|sub_0803DD34|
|unk_0803DD34|
	INCBIN	baserom.gba_0x3dd34_0x3dd38.extracted
	PUSH     {r0, r1, r2, r3}
	PUSH     {r4, r5, r6, lr}
	SUB      sp, #0x108
	ADD      r5, r0, #0
	ADD      r0, sp, #0x124
	ADD      r6, r1, #0
	STR      r0, [sp, #0x104]
	ADD      r4, sp, #4
	ADD      r0, r4, #0
	LDR      r1, [sp, #0x120]
	ADD      r2, sp, #0x104
	BL       |sub_0803DB7C|
	ADD      r2, r4, #0
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	BL       |loc_0803DCC4|
	ADD      sp, #0x108
	POP      {r4, r5, r6}
	POP      {r3}
	ADD      sp, #0x10
	BX       r3
