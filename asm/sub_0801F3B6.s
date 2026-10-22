	CODE16
|sub_0801F3B6|
|unk_0801F3B6|
		LDR r5, [r1]
		MOV r0, #0
		CMP r5, #0
		BLE      |loc_0801F3D8|
|loc_0801F3BE|
		LSL r3, r0, #3
		ADD r3, r3, r1
		ADD r3, #4
		LDRB r4, [r3, #4]
		CMP r4, r6
		BNE      |loc_0801F3D2|
		LDRB r3, [r3, #5]
		LDRB r4, [r2, #5]
		CMP r3, r4
		DCW     0xD0EF
|loc_0801F3D2|
		ADD r0, #1
		CMP r5, r0
		BGT      |loc_0801F3BE|
|loc_0801F3D8|
		ADD r0, r7, #0
		DCW     0xE7EA
