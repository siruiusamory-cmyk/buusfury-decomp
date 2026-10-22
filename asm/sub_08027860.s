	CODE16
|sub_08027860|
|unk_08027860|
		ADD r0, r4, #0
		ADD r0, #0x28
		LDR r1, [r6, #8]
		ADD r5, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_0802787C|
		ADD r0, r4, #0
		BL       |sub_0802770C|
		DCW     0xE7EF
|loc_0802787C|
		LDR r0, [sp, #0x38]
		CMP r0, #0
		DCW     0xD0EC
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		DCW     0xD0E9
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r7, sp
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0xac]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		LDMIA r5!, {r1, r2, r3, r5}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r5}
		MOV r5, #0
		ADD r3, sp, #0
		STRB r5, [r3]
		STR r4, [sp, #0x30]
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6, #4]
		BL       |loc_08011C70|
		CMP r0, #0
		DCW     0xD0D0
		LDR r6, [r6]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x68]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x68]
		ADD r3, r5, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
|loc_080278DC|
|unk_080278DC|
	INCBIN	baserom.gba_0x278dc_0x278de.extracted
|sub_080278DE|
|unk_080278DE|
	INCBIN	baserom.gba_0x278de_0x278e2.extracted
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_08027920|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_080278F2|
	MOV      r0, #0
	POP      {r3, pc}
