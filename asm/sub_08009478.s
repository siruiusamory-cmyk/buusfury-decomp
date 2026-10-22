	CODE16
|sub_08009478|
|unk_08009478|
		ADD r1, r4, #0
		MOV r0, #0
		BL       |inc_0x0158_0x143f2| + 0xd002
		ADD r5, r0, #0
		ADD r1, r0, #0
		LDR r0, [r7, #0xc]
		BL       |List_Append|
		LDR r0, [r4, #0x24]
		MOV r6, #1
		CMP r0, #1
		BLE      |loc_08009476|
|loc_08009492|
		LSL r1, r6, #1
		ADD r1, r1, r6
		LDR r0, [r4, #0x28]
		LSL r1, r1, #3
		ADD r1, r0, r1
		ADD r3, r6, #0
		ADD r2, r5, #0
		MOV r0, #0
		BL       |inc_0x0158_0x143f2| + 0xcf46
		ADD r1, r0, #0
		LDR r0, [r7, #0xc]
		BL       |List_Append|
		LDR r0, [r4, #0x24]
		ADD r6, #1
		CMP r0, r6
		BGT      |loc_08009492|
		B        |loc_08009476|
