	CODE16
|sub_08024406|
|unk_08024406|
		LDR r1, [pc, #0x164]
		LDR r1, [r1, #4]
		CMP r1, #0
		BEQ      |loc_08024426|
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		LDR r2, [r1, #0x1c]
		ADD r2, #1
		STR r2, [r1, #0x1c]
		CMP r2, #0x1e
		BLE      |loc_08024426|
		BL       |inc_0x03d784_0x041118| + 0x29fe
		MOV r0, #2
		DCW     0xE7EE
|loc_08024426|
		BL       |loc_080067F4|
		DCW     0xE7EB
