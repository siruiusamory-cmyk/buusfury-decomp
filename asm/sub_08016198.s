	CODE16
|sub_08016198|
|unk_08016198|
		LDR r0, [r4, #4]
		ADD r0, #0xff
		ADD r0, #1
		LDR r0, [r0, #0xc]
		LDR r1, [r4, #8]
		CMP r0, r1
		BEQ      |loc_080161AA|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0xda4
|loc_080161AA|
		LDR r0, [pc, #0x58]
		MOV r5, #0
		LDR r0, [r0]
		LDRH r0, [r0, #4]
		LSL r1, r0, #0x1a
		LSR r1, r1, #0x1f
		CMP r1, #0
		BEQ      |loc_080161DA|
		ADD r0, r4, #0
		BL       |sub_08015E94|
		LDR r0, [r4, #4]
		ADD r0, #0xff
		ADD r0, #1
		STR r5, [r0, #0x10]
		LDR r0, [r4, #4]
		LDR r1, [r0]
		LDR r2, [r1, #0x20]
		ADD r3, r2, r1
		LDR r2, [r4, #0x44]
		ADD r1, r4, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		B        |loc_080161FE|
|loc_080161DA|
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_080161FE|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0xb2a
		LDR r0, [r4, #4]
		ADD r0, #0xff
		ADD r0, #1
		STR r5, [r0, #0x10]
		LDR r0, [r4, #4]
		LDR r1, [r0]
		LDR r2, [r1, #0x20]
		ADD r3, r2, r1
		LDR r2, [r4, #0x44]
		ADD r1, r4, #0
		BL       |inc_0x046118_0x049114| + 0x98e
|loc_080161FE|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0xda4
|sub_08016202|
	DCW      0x0000
	DCW      0x8078
	DCW      0x086b
