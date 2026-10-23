	CODE16
|sub_0805072C|
|unk_0805072C|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x22ba
		LDR r0, [pc, #0x18]
		MOV r1, #0
		STR r0, [r4]
		MOV r0, #1
		LSL r0, r0, #0xa
		ADD r0, r4, r0
		ADD r0, #4
		STMIA r0!, {r1, r5}
		ADD r0, r4, #0
		B        |inc_0x049120_0x055620| + 0x760a
|sub_08050746|
	DCW      0x0000
	DCW      0x040c
	DCW      0x0000
|unk_0805074C|
	INCBIN	baserom.gba_0x5074c_0x5074e.extracted
	DCW      0x0804
