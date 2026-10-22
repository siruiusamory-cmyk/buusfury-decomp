	CODE16
|sub_08033808|
|unk_08033808|
		LDR r0, [r4, #0x10]
		LDR r5, [pc, #0x68]
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r4, #0
		BL       |Gfx_InitBlock2|
		LDR r0, [r4, #0x10]
		ADD r0, #1
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r4, #0
		BL       |Gfx_InitBlock1|
		B        |loc_08033836|
|loc_08033826|
|unk_08033826|
		CMP r0, #0xa0
		BGT      |loc_08033836|
		ADD r0, #0x70
		STRB r0, [r1, #2]
		LDR r0, [r4, #4]
		CMP r0, #0xa0
		BNE      |loc_08033836|
		STR r6, [r4, #4]
|loc_08033836|
|unk_08033836|
; cited by 0x080335D4 (a pc-relative load targets 0x0803383C)
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x646
	INCBIN  baserom.gba_0x3383a_0x33862.extracted
