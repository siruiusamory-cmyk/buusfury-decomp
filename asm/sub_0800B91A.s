	CODE16
|sub_0800B91A|
|unk_0800B91A|
		CMP r1, #8
		BLE      |inc_0x0158_0x143f2| + 0xb7c0
		MOV r1, #8
		STR r1, [r0, #0x28]
		MOV r1, #0
		STR r1, [r0, #0x14]
		B        |inc_0x0158_0x143f2| + 0xb7c0
