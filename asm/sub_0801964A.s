	CODE16
|sub_0801964A|
|unk_0801964A|
		CMP r1, #8
		BLE      |inc_0x153f2_0x1a3f2| + 0x4256
		MOV r1, #8
		STRB r1, [r0, #0x18]
		MOV r1, #0
		STRB r1, [r0, #0x17]
		B        |inc_0x153f2_0x1a3f2| + 0x4256
