	CODE16
|sub_08024E70|
|unk_08024E70|
		LSL r3, r0, #3
		SUB r0, r3, r0
		LDR r1, [pc, #0xb0]
		LSL r0, r0, #2
		ADD r0, r0, r1
		ADD r3, r2, #1
		BNE      |loc_08024E80|
		LDR r2, [r0, #4]
|loc_08024E80|
		LDRB r6, [r0, #0xd]
		STR r6, [sp, #4]
		LDRB r6, [r0, #0xe]
		LDRB r7, [r0, #0xf]
