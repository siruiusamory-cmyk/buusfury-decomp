	CODE16
|sub_08000568|
|unk_08000568|
		LSL r2, r2, #0x1f
		BEQ      |loc_0800057C|
		ADD r1, #0x1e
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
|loc_08000572|
		STRH r0, [r1]
		LDRH r2, [r1]
		CMP r2, r0
		BNE      |loc_08000572|
		B        |inc_0x0158_0x143f2| + 0x40c
|loc_0800057C|
		ADD r1, #0x1a
		LSL r0, r0, #0x10
		ASR r0, r0, #0x10
|loc_08000582|
		STRH r0, [r1]
		MOV r3, #0
		LDRSH r2, [r1, r3]
		CMP r2, r0
		BNE      |loc_08000582|
		B        |inc_0x0158_0x143f2| + 0x40c
