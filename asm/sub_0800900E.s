	CODE16
|sub_0800900E|
|unk_0800900E|
; cited by 0x08008D80 (a pc-relative load targets 0x08009018)
		LDR r0, [sp, #0x30]
		STR r5, [r0]
		LDR r0, [sp, #0x34]
		STR r6, [r0]
		B        |inc_0x0158_0x143f2| + 0x8eb2
	INCBIN  baserom.gba_0x9018_0x9022.extracted
