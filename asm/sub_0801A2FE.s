	CODE16
|sub_0801A2FE|
|unk_0801A2FE|
; cited by 0x08019FEC (a pc-relative load targets 0x0801A310)
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		B        |inc_0x153f2_0x1a3f2| + 0x4f08
	INCBIN  baserom.gba_0x1a30e_0x1a322.extracted
