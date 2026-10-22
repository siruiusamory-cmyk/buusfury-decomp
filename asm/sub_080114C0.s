	CODE16
|sub_080114C0|
|unk_080114C0|
		ADD r2, r1, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x11258
		B        |inc_0x0158_0x143f2| + 0x11366
|loc_080114CC|
|unk_080114CC|
		CMP r0, #0
		BNE      |loc_080114EC|
		LDRH r0, [r7, #4]
		LDRH r1, [r5, #4]
		ADD r0, r0, r1
		STRH r0, [r7, #4]
		LDRB r0, [r5, #6]
		ADD r1, r6, #0
		STRB r0, [r7, #6]
		LDRB r0, [r5, #7]
		LDR r2, [sp]
		STRB r0, [r2, #7]
		ADD r0, r4, #0
		BL       |loc_0801137C|
		B        |inc_0x0158_0x143f2| + 0x11366
|loc_080114EC|
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x111ee
		B        |inc_0x0158_0x143f2| + 0x11366
|loc_080114F6|
|unk_080114F6|
		LDR r2, [sp]
		LDRB r0, [r2]
		CMP r0, #0
		BNE      |loc_0801150A|
		ADD r2, r1, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x11258
		B        |inc_0x0158_0x143f2| + 0x11366
|loc_0801150A|
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x111ee
		B        |inc_0x0158_0x143f2| + 0x11366
|loc_08011514|
|unk_08011514|
; cited by 0x08011204 (a pc-relative load targets 0x08011554)
		LDRB r2, [r5, #7]
		MOV r1, #0xff
		CMP r2, #0xff
		BEQ      |loc_0801154A|
		LSL r3, r2, #2
		ADD r2, r3, r2
		LSL r2, r2, #1
		ADD r2, r2, r4
		ADD r0, r2, r0
		LDRB r2, [r0]
		CMP r2, #0
		BNE      |loc_08011540|
		LDRH r2, [r0, #4]
		LDRH r3, [r5, #4]
		ADD r2, r2, r3
		STRH r2, [r0, #4]
		STRB r1, [r0, #6]
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |loc_0801137C|
		B        |inc_0x0158_0x143f2| + 0x11366
|loc_08011540|
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x111ee
		B        |inc_0x0158_0x143f2| + 0x11366
|loc_0801154A|
		STRB r6, [r4]
		STRB r1, [r5, #8]
		STRB r1, [r5, #9]
		B        |inc_0x0158_0x143f2| + 0x11366
	INCBIN  baserom.gba_0x11552_0x1155a.extracted
