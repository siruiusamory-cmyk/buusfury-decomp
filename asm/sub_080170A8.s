	CODE16
|sub_080170A8|
|unk_080170A8|
		LDR r6, [pc, #0x58]
		ADD r4, r0, #0
		ADD r4, #0xff
		LSL r1, r1, #0x19
		LSR r1, r1, #0x1f
		ADD r4, #1
		SUB r6, #0xc
		CMP r1, #0
		BEQ      |loc_080170D2|
		ADD r1, r6, #0
		ADD r3, r7, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0x14]
		ADD r0, #3
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1e
		STR r0, [r4, #0x14]
		STR r7, [r4, #0x10]
|loc_080170D2|
		LDR r0, [pc, #0x2c]
		LDR r0, [r0]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1f
		BEQ      |loc_080170F6|
		ADD r1, r6, #0
		ADD r3, r7, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0x14]
		ADD r0, #1
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1e
		STR r0, [r4, #0x14]
		STR r7, [r4, #0x10]
|loc_080170F6|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x1cb4
