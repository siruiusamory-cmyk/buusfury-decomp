	CODE16
|sub_0800AD5E|
|unk_0800AD5E|
; cited by 0x0800AB66 (a pc-relative load targets 0x0800AD7C)
		ADD r3, r5, #0
		ADD r2, r6, #0
		MOV r0, #0
		STR r7, [sp]
		LDR r1, [sp, #4]
		BL       |inc_0x0158_0x143f2| + 0xaa70
		ADD r5, r0, #0
		ADD r1, r0, #0
		LDR r0, [r4]
		BL       |List_Append|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0xac02
	INCBIN  baserom.gba_0xad7a_0xad82.extracted
