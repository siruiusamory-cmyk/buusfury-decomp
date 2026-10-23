	CODE16
|sub_0802CD42|
|unk_0802CD42|
		MOV r0, #0xff
		ADD r0, #2
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0802CD60|
		MOV r0, #0xb2
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_0802CD40|
|loc_0802CD60|
		MOV r0, #0x56
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0802CD40|
		MOV r0, #0xac
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x2cd76_0x2cd78.extracted
|sub_0802CD78|
|unk_0802CD78|
	INCBIN	baserom.gba_0x2cd78_0x2cd7c.extracted
	LDR      r0, [pc, #0]
	BX       lr
|sub_0802CD80|
|unk_0802CD80|
	INCBIN	baserom.gba_0x2cd80_0x2cd82.extracted
|sub_0802CD82|
	DCW      0x0300
