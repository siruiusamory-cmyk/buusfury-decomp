	CODE16
|sub_08039EEC|
|unk_08039EEC|
; cited by 0x08039DB6 (a pc-relative load targets 0x08039F10)
		LDR r4, [r1]
		LDR r5, [r0, #0xc]
		ADD r4, r4, r5
		STR r4, [r1]
		LDR r4, [r1, #4]
		LDR r3, [r0, #0x10]
		ADD r3, r4, r3
		STR r3, [r1, #4]
		LDR r1, [r2]
		LDR r0, [r0, #0x14]
		ADD r0, r1, r0
		STR r0, [r2]
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x4d28
	INCBIN  baserom.gba_0x39f08_0x39f16.extracted
|sub_08039F16|
	DCW      0x3e22
