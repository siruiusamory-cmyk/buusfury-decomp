	CODE16
|loc_0800776C|
	LDR      r0, [pc, #0]
	BX       lr
|sub_08007770|
|unk_08007770|
; cited by 0x0800776C (a pc-relative load targets 0x08007770)
	INCBIN  baserom.gba_0x7770_0x7774.extracted
		ADD r1, r0, #0
		LDR r0, [pc, #0x30]
		LDR r0, [r0]
		ADD r0, #0xc0
		LDR r2, [r0, #4]
		LDR r0, [r1, #4]
		ADD r0, #1
		CMP r2, r0
		BEQ      |sub_0800778A|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x7634
