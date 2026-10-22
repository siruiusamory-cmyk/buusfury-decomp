	CODE16
|sub_08029DCE|
|unk_08029DCE|
		ADD r1, r4, #0
		ADD r5, sp, #0x14
		ADD r0, r5, #0
		BL       |sub_0800FDFA|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		ADD r2, r6, #4
		STR r2, [sp, #0x24]
		STR r0, [sp, #0x28]
		LDR r1, [r0]
		LDR r3, [r6, #4]
		ADD r7, r2, #4
		ADD r1, r1, r3
		STR r1, [r0]
		LDR r1, [r0, #4]
		LDR r2, [r6, #8]
		ADD r6, sp, #4
		ADD r1, r1, r2
		STR r1, [r0, #4]
		ADD r1, r4, #0
		ADD r0, r6, #0
		BL       |sub_0800FDFA|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #1
		ADD r1, r5, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x50]
		ADD r2, r2, r1
		ADD r1, r6, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_08029E34|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #0
		ADD r1, r6, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		B        |loc_08029E58|
|loc_08029E34|
		LDR r0, [sp, #0x28]
		LDR r2, [sp, #0x24]
		LDR r1, [r0]
		LDR r2, [r2]
		SUB r1, r1, r2
		STR r1, [r0]
		LDR r1, [r0, #4]
		LDR r2, [r7]
		SUB r1, r1, r2
		STR r1, [r0, #4]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #0
		ADD r1, r5, #0
		BL       |inc_0x046118_0x049114| + 0x98e
|loc_08029E58|
		MOV r0, #0
		DCW     0xE7B6
