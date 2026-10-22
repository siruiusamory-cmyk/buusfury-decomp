	CODE16
|sub_0800E29A|
|unk_0800E29A|
		LDRH r3, [r1]
		ADD r3, r3, r5
		LSL r5, r3, #0x10
		ASR r5, r5, #0x10
|loc_0800E2A2|
		STRH r5, [r1]
		MOV r3, #0
		LDRSH r6, [r1, r3]
		CMP r6, r5
		BNE      |loc_0800E2A2|
|loc_0800E2AC|
|unk_0800E2AC|
		ADD r1, r2, #0
		ADD r1, #0x16
		ADD r2, #0x18
		MOV r3, #0
		LDRSH r2, [r2, r3]
		LDR r3, [pc, #0xf4]
		MUL r2, r3
		ASR r2, r2, #0x10
		MOV r3, #0
		LDRSH r5, [r1, r3]
		ADD r5, r5, r2
		MOV r3, #2
		LDRSH r6, [r1, r3]
		CMP r5, r6
		BLE      |sub_0800E2D0|
		LDRH r2, [r1, #2]
		STRH r2, [r1]
		B        |loc_0800E2E2|
