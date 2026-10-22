	CODE16
|sub_0800E24A|
|unk_0800E24A|
		LDRH r2, [r0]
		ADD r1, r2, r1
		LSL r1, r1, #0x10
		ASR r1, r1, #0x10
|loc_0800E252|
		STRH r1, [r0]
		MOV r3, #0
		LDRSH r2, [r0, r3]
		CMP r2, r1
		BNE      |loc_0800E252|
