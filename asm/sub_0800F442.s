	CODE16
|sub_0800F442|
|unk_0800F442|
		CMP r1, #0xb
		BEQ      |inc_0x0158_0x143f2| + 0xf320
		CMP r1, #0xf
		BNE      |loc_0800F4AC|
		LDR r0, [r4, #0x14]
		LDR r1, [r0]
		LDR r2, [r1, #0x10]
		ADD r2, r2, r1
		ADD r1, r4, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf2e8
|loc_0800F45C|
|unk_0800F45C|
		LDR r1, [r4, #0x58]
		LDR r1, [r1, #0x50]
		CMP r1, #0
		BEQ      |loc_0800F468|
		BL       |inc_0x049120_0x055620| + 0x6d00
|loc_0800F468|
		LDR r0, [r4, #0x5c]
		CMP r0, #0
		BEQ      |loc_0800F474|
		LDR r0, [r0, #8]
		BL       |inc_0x049120_0x055620| + 0x6d00
|loc_0800F474|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0xf2e8
		LDR r1, [r4, #0x58]
		LDR r1, [r1, #0x50]
		CMP r1, #0
		BEQ      |loc_0800F488|
		MOV r2, #0x80
		LDR r1, [pc, #0x38]
		BL       |Gfx_BeginTileLoad1|
|loc_0800F488|
		LDR r0, [r4, #0x5c]
		CMP r0, #0
		BEQ      |loc_0800F498|
		LDRH r2, [r0, #2]
		LDR r1, [r0, #4]
		LDR r0, [r0, #8]
		BL       |Gfx_BeginTileLoad1|
|loc_0800F498|
		MOV r0, #0
		STR r5, [r4, #0x30]
		B        |inc_0x0158_0x143f2| + 0xf2e8
