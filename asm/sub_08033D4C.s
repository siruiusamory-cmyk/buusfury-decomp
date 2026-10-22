	CODE16
|sub_08033D4C|
|unk_08033D4C|
		CMP r5, #1
		BNE      |loc_08033D5C|
		LDRB r1, [r4, #0x11]
		CMP r1, #0
		BNE      |loc_08033D5C|
		ADD r1, r4, #0
		BL       |sub_08033BC4|
|loc_08033D5C|
		STRB r5, [r4, #0x11]
		B        |inc_0x331c0_0x341c0| + 0xb8a
	INCBIN  baserom.gba_0x33d60_0x33d66.extracted
