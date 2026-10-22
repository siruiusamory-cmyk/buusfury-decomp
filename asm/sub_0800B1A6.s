	CODE16
|sub_0800B1A6|
|unk_0800B1A6|
		LDR r0, [pc, #0x170]
		LDR r1, [pc, #0x170]
		STR r0, [r4]
		STR r1, [r4, #0xc]
		LDR r0, [pc, #0x170]
		MOV r1, #0xa0
		STR r0, [r4]
		ADD r0, #0x30
		STR r0, [r4, #0xc]
		ADD r0, r4, #0
		ADD r0, #0x80
		MOV r2, #0x40
		ADD r5, r0, #0
		BL       |loc_0803F540|
		STR r6, [r4, #0x14]
		MOV r6, #0
		STR r6, [r4, #0x28]
		STR r6, [r4, #0x1c]
		LDR r1, [sp, #0x20]
		MOV r0, #1
		LDR r2, [r1]
		LDR r1, [r1, #4]
		STR r0, [r4, #0x2c]
		STR r1, [r4, #0x60]
		STR r2, [r4, #0x5c]
		STR r6, [r4, #0x20]
		STR r6, [r4, #0x34]
		STR r6, [r4, #0x38]
		STR r6, [r4, #0x48]
		STRB r6, [r4, #8]
		STR r6, [r4, #4]
		LDR r1, [pc, #0x128]
		STR r6, [r4, #0x58]
		LDR r1, [r1, #0xc]
		MOV r2, #8
		STR r1, [r5, #0xc]
		MOV r1, #0xf
		STRB r1, [r5, #1]
		LDR r1, [sp, #0x18]
		SUB r0, r5, r2
		BL       |Thunk_PaletteCopy|
		STR r6, [r4, #0x24]
		CMP r7, #0
		BEQ      |loc_0800B27C|
		MOV r0, #1
		STR r0, [r4, #0x24]
		MOV r0, #0xe0
		STR r0, [r4, #0x54]
		MOV r6, #0x40
		STR r6, [r5, #0x28]
		LSL r0, r6, #6
		STR r0, [r5, #0x30]
		STR r6, [r5, #0x2c]
		STR r6, [r5, #0x18]
		STR r6, [r5, #0x1c]
		LDR r1, [r5, #0x24]
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x1bc
		MOV r0, #0x7e
		LDRH r0, [r0, r4]
		LDR r1, [pc, #0xfc]
		STR r6, [sp, #0xc]
		LSL r0, r0, #5
		ADD r1, r0, r1
		MOV r0, #0
		STR r0, [sp, #4]
		STR r0, [sp, #8]
		ADD r0, r5, #0
		STR r6, [sp, #0x10]
		ADD r2, sp, #4
		BL       |sub_0804915C|
		MOV r0, #0xa0
		STR r0, [r5, #0x28]
		STR r6, [r5, #0x2c]
		LSL r0, r0, #6
		STR r0, [r5, #0x30]
		LDR r0, [r5, #0x28]
		STR r0, [r5, #0x18]
		STR r6, [r5, #0x1c]
		LDR r0, [sp, #0x40]
		CMP r0, #0
		LDR r0, [r4, #0x5c]
		BEQ      |loc_0800B268|
		SUB r0, #0x70
		ADD r1, r0, r6
		STR r0, [r4, #0x74]
		STR r1, [r4, #0x68]
		ADD r1, r0, #0
		ADD r1, #0x80
		ADD r0, #0xc0
		STR r0, [r4, #0x70]
		STR r1, [r4, #0x6c]
		B        |loc_0800B290|
|loc_0800B268|
		SUB r0, #0x70
		ADD r1, r0, #0
		ADD r1, #0x40
		STR r0, [r4, #0x68]
		STR r1, [r4, #0x6c]
		ADD r1, #0x40
		ADD r0, #0xa0
		STR r0, [r4, #0x74]
		STR r1, [r4, #0x70]
		B        |loc_0800B290|
|loc_0800B27C|
		MOV r0, #0xa0
		STR r0, [r4, #0x54]
		LDR r0, [r4, #0x5c]
		SUB r0, #0x50
		ADD r1, r0, #0
		ADD r1, #0x40
		STR r0, [r4, #0x68]
		STR r1, [r4, #0x6c]
		ADD r0, #0x80
		STR r0, [r4, #0x70]
|loc_0800B290|
		LDR r0, [sp, #0x38]
		LDR r1, [pc, #0x7c]
		LSL r3, r0, #2
		ADD r0, r3, r0
		LSL r0, r0, #2
		ADD r1, #0x10
		ADD r0, r0, r1
		STR r0, [r4, #0x4c]
		LDR r1, [r5, #0x24]
		LDR r0, [r0, #0x10]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		MOV r0, #2
		STRB r0, [r5, #3]
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xac48
		MOV r0, #1
		STR r0, [r4, #0x50]
		LDR r0, [pc, #0x70]
		STR r0, [r5, #0x34]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xb04a
