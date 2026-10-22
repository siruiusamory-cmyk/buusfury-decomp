	CODE16
|sub_0803D0D4|
|unk_0803D0D4|
		LDR r3, [r2, #0x58]
		LDR r4, [r3, #0x78]
		LDR r2, [r2, #0x50]
		CMP r4, r2
		BNE      |loc_0803D0E4|
		BL       |inc_0x351c0_0x3d4d0| + 0x7d86
		B        |inc_0x351c0_0x3d4d0| + 0x7f36
|loc_0803D0E4|
		ADD r3, #0x4c
		LDR r3, [r3, #0x54]
		CMP r3, r2
		BNE      |inc_0x351c0_0x3d4d0| + 0x7f32
	INCBIN  baserom.gba_0x3d0ec_0x3d0ee.extracted
|sub_0803D0EE|
|unk_0803D0EE|
	INCBIN	baserom.gba_0x3d0ee_0x3d0f2.extracted
	BL       |loc_0803CFC2|
	MOV      r0, #0
	POP      {r4, pc}
|sub_0803D0FA|
|unk_0803D0FA|
; cited by 0x0803CEA4 (a pc-relative load targets 0x0803D100)
	INCBIN	baserom.gba_0x3d0fa_0x3d10c.extracted
