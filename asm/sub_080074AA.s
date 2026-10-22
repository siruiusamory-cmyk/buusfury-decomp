	CODE16
|sub_080074AA|
|unk_080074AA|
; cited by 0x08007484 (a pc-relative load targets 0x080074BC)
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x9994
		LDR r0, [pc, #8]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x7350
	INCBIN  baserom.gba_0x74ba_0x74bc.extracted
		DCD     0x08049794
	INCBIN  baserom.gba_0x74c0_0x74c2.extracted
