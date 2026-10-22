	CODE16
|loc_08006C8A|
|unk_08006C8A|
		LSL r0, r4, #2
		ADD r0, r0, r6
		LDR r1, [r0, #4]
		LDR r7, [sp]
		MOV r0, #0
		LDR r3, [r7]
		CMP r3, #0
		BLE      |inc_0x0158_0x143f2| + 0x6b64
|loc_08006C9A|
		LSL r2, r0, #2
		ADD r2, r2, r7
		LDR r2, [r2, #4]
		CMP r2, r1
		BEQ      |sub_08006CAC|
		ADD r0, #1
		CMP r3, r0
		BGT      |loc_08006C9A|
		B        |inc_0x0158_0x143f2| + 0x6b64
