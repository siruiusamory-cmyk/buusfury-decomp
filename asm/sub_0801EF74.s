	CODE16
|sub_0801EF74|
|unk_0801EF74|
		ADD r0, #0xff
		ADD r0, #1
		LDR r0, [r0, #0x1c]
		CMP r0, #0
		BLE      |loc_0801EF80|
		ADD r1, r0, #0
|loc_0801EF80|
		ADD r0, r1, #0
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		DCW     0xE7F3
|loc_0801EF8A|
|unk_0801EF8A|
		MOV r0, #0
		DCW     0xE7F1
		PUSH {r3, r4, r5, r6, r7, lr}
		LDR r2, [pc, #0xd0]
		ADD r5, r0, #0
		LDR r0, [r2]
		ADD r4, r5, #0
		LDRH r0, [r0, #2]
		ADD r4, #0xff
		ADD r4, #1
		LSL r1, r0, #0x1a
		LSR r1, r1, #0x1f
		MOV r6, #0
		CMP r1, #0
		BNE      |loc_0801EFBC|
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BNE      |loc_0801EFBC|
		MOV r0, #0xa
		STR r0, [r4, #0x28]
		STR r6, [r4, #0x2c]
		MOV r0, #1
		STR r0, [r4, #0x24]
		STR r6, [r4, #0x20]
		B        |loc_0801F056|
|loc_0801EFBC|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		BNE      |sub_0801F052|
		LDR r0, [r4, #0x20]
		ADD r0, #1
		STR r0, [r4, #0x20]
		CMP r0, #0x32
		BLE      |loc_0801EFF8|
		LDR r7, [r4, #0x24]
		CMP r7, #1
		BNE      |loc_0801EFE4|
		LDR r0, [r4, #0x1c]
		BL       |sub_08053034|
		CMP r0, #0
		BNE      |loc_0801EFE4|
		MOV r0, #0xa
		STR r0, [r4, #0x24]
		STR r6, [r4, #0x20]
		B        |loc_0801EFF8|
|loc_0801EFE4|
		CMP r7, #0xa
		BNE      |loc_0801EFF8|
		LDR r0, [r4, #0x1c]
		BL       |sub_08053058|
		CMP r0, #0
		BNE      |loc_0801EFF8|
		MOV r0, #0x64
		STR r0, [r4, #0x24]
		STR r6, [r4, #0x20]
|loc_0801EFF8|
		LDR r2, [pc, #0x68]
		LDR r0, [r2]
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x1a
		LSR r0, r0, #0x1f
		BEQ      |loc_0801F014|
		LDR r0, [r4, #0x1c]
		LDR r1, [r4, #0x24]
		CMP r0, r1
		BLE      |loc_0801F012|
		SUB r0, r0, r1
		STR r0, [r4, #0x1c]
		B        |loc_0801F014|
|loc_0801F012|
		STR r6, [r4, #0x1c]
|loc_0801F014|
		LDR r0, [r2]
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		DCW     0xD00D
		LDR r0, [r4, #0x1c]
		LDR r1, [r4, #0x24]
		LDR r3, [pc, #0x54]
		ADD r2, r0, r1
		LDR r1, [r4, #0x14]
		ADD r0, r3, #0
		CMP r1, r3
		BHS      |loc_0801F030|
		ADD r0, r1, #0
|loc_0801F030|
		CMP r2, r0
		BHS      |sub_0801F038|
		STR r2, [r4, #0x1c]
		DCW     0xE000
