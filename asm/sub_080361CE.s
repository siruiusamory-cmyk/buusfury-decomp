	CODE16
|sub_080361CE|
|unk_080361CE|
		ADD r1, r5, #0
		ADD r0, sp, #0x64
		BL       |loc_0800FE78|
		ADD r1, r4, #0
		ADD r0, sp, #0x54
		BL       |loc_0800FE78|
		LDR r0, [sp, #0x54]
		LDR r1, [sp, #0x5c]
		LDR r2, [sp, #0x60]
		ADD r0, r0, r1
		LDR r1, [sp, #0x58]
		STR r0, [sp, #0x44]
		ADD r1, r1, r2
		ASR r3, r1, #1
		ASR r0, r0, #1
		STR r1, [sp, #0x48]
		STR r3, [sp, #0x48]
		STR r0, [sp, #0x44]
		STR r0, [sp, #0x4c]
		STR r3, [sp, #0x50]
		LDRB r0, [r4, #0x10]
		LDR r1, [sp, #0x6c]
		LDR r2, [sp, #0x70]
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x64]
		ADD r1, r0, r1
		LDR r0, [sp, #0x68]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x10]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0xc]
		LDR r1, [sp, #0x4c]
		LDR r2, [sp, #0x50]
		SUB r0, r0, r1
		LDR r1, [sp, #0x10]
		STR r0, [sp, #4]
		SUB r6, r1, r2
		ADD r1, r0, #0
		CMP r0, #0
		STR r6, [sp, #8]
		BGE      |loc_08036232|
		NEG r1, r0
|loc_08036232|
		ADD r2, r6, #0
		CMP r6, #0
		BGE      |loc_0803623A|
		NEG r2, r2
|loc_0803623A|
		CMP r1, r2
		BLE      |inc_0x351c0_0x3d4d0| + 0x10aa
		STR r3, [sp, #0x20]
|loc_08036240|
|unk_08036240|
		LDR r1, [sp, #0x60]
		ADD r1, #3
		STR r1, [sp, #0x28]
		CMP r0, #0
		BLE      |loc_0803625A|
		MOV r0, #3
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x4c]
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x5c]
		ADD r0, #3
		STR r0, [sp, #0x24]
		B        |loc_0803629A|
|loc_0803625A|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x54]
		SUB r0, #4
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x4c]
		STR r0, [sp, #0x24]
		B        |loc_0803629A|
		ADD r1, r4, #0
		ADD r0, sp, #4
		BL       |sub_0800FDFA|
		LDR r0, [sp, #4]
		CMP r6, #0
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0xc]
		STR r0, [sp, #0x24]
		BLE      |loc_0803628E|
		MOV r6, #0
		STRB r6, [r4, #0x10]
		LDR r0, [sp, #0x58]
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x60]
		SUB r0, #6
		STR r0, [sp, #0x28]
		B        |loc_0803629A|
|loc_0803628E|
		MOV r0, #1
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x58]
		STR r0, [sp, #0x20]
		LDR r0, [sp, #8]
		STR r0, [sp, #0x28]
