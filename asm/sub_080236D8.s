	CODE16
|sub_080236D8|
|unk_080236D8|
		LDR r0, [pc, #0xf8]
		DCW     0xF019
		DCW     0xFF6D
		ADD r4, r0, #0
		DCW     0xD03D
		LDR r0, [pc, #0xc8]
		ADD r1, r4, #0
		STR r0, [r4]
		MOV r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r0, [r4, #4]
		STR r0, [r1, #0xc]
		STR r0, [r1, #8]
		STR r0, [r1, #0x10]
		LDR r1, [pc, #0xe0]
		STR r1, [r4]
		MOV r1, #0xff
		ADD r1, #0x95
		STR r0, [r1, r4]
		LDR r1, [pc, #0xa0]
		ADD r1, r4, r1
		STR r0, [r1]
		LDR r0, [pc, #0xd4]
		ADD r0, r4, r0
		BL       |loc_08004838|
		LDR r0, [pc, #0xd0]
		LDR r6, [pc, #0xd0]
		ADD r5, r4, r0
		ADD r1, r5, #0
		ADD r1, #0x3a
		ADD r0, r5, #0
		MOV r2, #2
		ADD r3, r6, #0
		ADD r0, #0x2e
		BL       |__vecmap1c__FPvT1iPFPv_v|
		LDR r7, [pc, #0xc0]
		ADD r3, r7, #0
		MOV r2, #4
		DCW     0xE000
|loc_0802372C|
|unk_0802372C|
		B        |loc_08023768|
		ADD r1, r5, #0
		ADD r1, #0x4c
		ADD r0, r5, #0
		ADD r0, #0x3c
		BL       |__vecmap1c__FPvT1iPFPv_v|
		LDR r0, [pc, #0xb0]
		ADD r3, r6, #0
		ADD r5, r4, r0
		ADD r1, r5, #0
		ADD r1, #0x3a
		ADD r0, r5, #0
		MOV r2, #2
		ADD r0, #0x2e
		BL       |__vecmap1c__FPvT1iPFPv_v|
		ADD r1, r5, #0
		ADD r1, #0x4c
		ADD r3, r7, #0
		MOV r2, #4
		ADD r0, r5, #0
		ADD r0, #0x3c
		BL       |__vecmap1c__FPvT1iPFPv_v|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #0
		DCW     0xE7B6
