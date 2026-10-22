	CODE16
|sub_08047F94|
|unk_08047F94|
		MOV r0, #0x1f
		LSL r0, r0, #0x1a
		AND r4, r0
		ADD r1, r4, #0
		MOV r0, #2
		BL       |sub_08047FD4|
		MOV r0, #0
		MOV r1, #0
		STMIA r5!, {r0, r1}
		ADD r1, sp, #4
		LDMIA r1!, {r0, r1}
		DCW     0xE7EE
	INCBIN  baserom.gba_0x47fae_0x47fb0.extracted
