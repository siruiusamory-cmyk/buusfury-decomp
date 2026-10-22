	CODE16
|loc_08006CFC|
|unk_08006CFC|
		LDR r1, [sp, #4]
		LSL r0, r4, #2
		ADD r0, r0, r1
		LDR r1, [r0, #4]
		LDR r7, [sp, #8]
		MOV r0, #0
		LDR r3, [r7]
		CMP r3, #0
		BLE      |inc_0x0158_0x143f2| + 0x6bda
|loc_08006D0E|
		LSL r2, r0, #2
		ADD r2, r2, r7
		LDR r2, [r2, #4]
		CMP r2, r1
		BEQ      |sub_08006D20|
		ADD r0, #1
		CMP r3, r0
		BGT      |loc_08006D0E|
		B        |inc_0x0158_0x143f2| + 0x6bda
