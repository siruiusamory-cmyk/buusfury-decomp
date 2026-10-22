	CODE16
|sub_08006A5C|
|unk_08006A5C|
		LDR r0, [pc, #0x4c]
		LDR r0, [r0]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_08006AA4|
		LDR r0, [r4, #0xc]
		LDR r1, [r0]
		LDR r2, [r1, #0xc]
		ADD r2, r2, r1
		LDR r1, [r4, #0x1c]
		BL       |Thunk_JumpRegister1|
		CMP r0, r5
		BLE      |loc_08006AA4|
		ADD r1, r6, #0
		MOV r6, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0xc]
		LDR r1, [r0]
		LDR r2, [r1, #4]
		ADD r3, r2, r1
		ADD r2, r5, #1
		LDR r1, [r4, #0x1c]
		BL       |inc_0x046118_0x049114| + 0x98e
		LDR r0, [r4, #4]
		ADD r0, #0xff
		ADD r0, #1
		STR r6, [r0, #0x10]
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x6902
|loc_08006AA4|
|unk_08006AA4|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x6902
	INCBIN  baserom.gba_0x6aa8_0x6aaa.extracted
