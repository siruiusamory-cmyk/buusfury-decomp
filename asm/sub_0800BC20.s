	CODE16
|sub_0800BC20|
|unk_0800BC20|
		B        |inc_0x0158_0x143f2| + 0xbb68
|loc_0800BC22|
|unk_0800BC22|
		BLT      |inc_0x0158_0x143f2| + 0xbab2
|loc_0800BC24|
|unk_0800BC24|
		MOV r3, #5
		LSL r3, r3, #8
		ADD r3, sp
		LDRB r0, [r3, #4]
		CMP r0, #0x48
		BGE      |inc_0x0158_0x143f2| + 0xbb36
		LDR r2, [pc, #0x54]
		MOV r6, #1
|loc_0800BC34|
|unk_0800BC34|
; cited by 0x0800B868 (a pc-relative load targets 0x0800BC48)
		LSL r1, r0, #3
		LDR r3, [r2, r1]
		ADD r1, r1, r2
		STRB r6, [r5, r3]
		LDR r1, [r1, #4]
		ADD r0, #1
		CMP r0, #0x48
		STRB r6, [r5, r1]
		B        |inc_0x0158_0x143f2| + 0xbb34
	INCBIN  baserom.gba_0xbc46_0xbc5a.extracted
