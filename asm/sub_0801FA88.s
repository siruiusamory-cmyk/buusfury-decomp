	CODE16
|sub_0801FA88|
|unk_0801FA88|
		LDR r0, [r4, #0x28]
		LSL r0, r0, #3
		ADD r0, r0, r6
		ADD r0, #4
		LDR r1, [r0]
		CMP r1, #1
		BNE      |loc_0801FA9A|
		MOV r0, #1
		B        |loc_0801FAD8|
|loc_0801FA9A|
		STR r0, [sp, #4]
		MOV r0, #0xff
		ADD r0, #0x39
		DCD     0xFD8AF01D
		CMP r0, #0
		BEQ      |loc_0801FAD4|
		LDR r1, [pc, #0xbc]
		MOV r2, #0
		STMIA r0!, {r1, r2}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r2, [r1, #0xc]
		STR r2, [r1, #8]
		STR r2, [r1, #0x10]
		LDR r1, [pc, #0xac]
		STR r1, [r0]
		LDR r3, [sp, #4]
		ADD r1, r0, #0
		LDRH r2, [r3]
		ADD r1, #0xff
		ADD r1, #0x15
		STRH r2, [r1]
		LDRH r2, [r3, #2]
		STRH r2, [r1, #2]
		LDRH r2, [r3, #4]
		STRH r2, [r1, #4]
|loc_0801FAD4|
		BL       |inc_0x03d784_0x041118| + 0x11c
|loc_0801FAD8|
		STR r0, [sp, #8]
		CMP r0, #0
		BLE      |loc_0801FA82|
		LDR r1, [pc, #0x84]
		MOV r3, #0
		MOV r2, #0x40
		ADD r1, #0xc
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r2, [sp, #8]
		ADD r1, r5, #0
		STR r2, [sp]
		ADD r1, #0xff
		ADD r1, #0x2d
		ADD r2, r6, #0
		ADD r0, r5, #0
		LDR r3, [r4, #0x28]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x360e
		LDR r1, [r6]
		LDR r0, [r4, #0x28]
		CMP r1, r0
		BGT      |loc_0801FA82|
		CMP r0, #0
		BEQ      |loc_0801FB12|
		SUB r0, #1
		STR r0, [r4, #0x28]
		B        |loc_0801FA82|
|loc_0801FB12|
		MOV r3, #0
		ADD r5, #0xff
		ADD r5, #0x11
		STRB r3, [r5, #4]
		B        |loc_0801FA82|
|loc_0801FB1C|
|unk_0801FB1C|
		LDR r0, [r4, #0x28]
		CMP r0, #0
		BEQ      |loc_0801FB32|
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0x28]
		SUB r0, #1
		STR r0, [r4, #0x28]
|loc_0801FB32|
		MOV r2, #0
		STR r2, [r4, #0x10]
		B        |loc_0801FA82|
	INCBIN  baserom.gba_0x1fb38_0x1fb3a.extracted
