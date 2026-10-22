	CODE16
|sub_0802C8BE|
|unk_0802C8BE|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_0802C8F0|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0802C8F0|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_0802C8F0|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_0802C8F0|
		ADD r1, r0, #0
		LDR r0, [pc, #0x20]
		SUB r0, #8
		LDR r0, [r0]
		BL       |loc_08011944|
		MOV r0, #1
		B        |inc_0x2bb4c_0x2d1c0| + 0xd70
|loc_0802C8F0|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xd70
|loc_0802C8F4|
|unk_0802C8F4|
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		B        |inc_0x2bb4c_0x2d1c0| + 0xd70
	INCBIN  baserom.gba_0x2c8fa_0x2c8fe.extracted
