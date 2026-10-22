|Irq_WriteEnable3|
	CODE16
|unk_0803D7BE|
		LDR r5, [pc, #0x16c]
		LDR r0, [r5, #8]
		BL       |Struct_ZeroFields|
		DCW     0xF7FF
		DCW     0xFE83
		LDR r0, [r5, #4]
		BL       |inc_0x03d784_0x041118| + 0x1c56
		BL       |inc_0x03d784_0x041118| + 0x2954
		LDR r1, [pc, #0x15c]
		LDR r0, [r5, #4]
		LDR r2, [pc, #0x15c]
		STR r1, [r0]
		LDRH r1, [r2]
		MOV r0, #1
		ORR r0, r1
		STRH r0, [r2]
		LDR r0, [r5, #0xc]
		BL       |inc_0x03d784_0x041118| + 0x1a34
		LDR r0, [r5]
		BL       |Irq_WriteMaster2|
		LDR r0, [r5, #8]
		BL       |loc_0803D4A0|
		ADD r0, r4, #0
		B        |inc_0x03d784_0x041118| + 0x38
