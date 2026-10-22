	CODE16
|sub_0803BFE6|
|unk_0803BFE6|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		B        |inc_0x351c0_0x3d4d0| + 0x6e22
|loc_0803BFEC|
|unk_0803BFEC|
		MOV r1, #0
		CMP r2, #0
		BLE      |loc_0803BFF6|
		STRB r1, [r4, #0x10]
		B        |inc_0x351c0_0x3d4d0| + 0x6e22
|loc_0803BFF6|
		MOV r0, #1
		STRB r0, [r4, #0x10]
		B        |inc_0x351c0_0x3d4d0| + 0x6e22
