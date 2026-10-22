	CODE16
|sub_0801341C|
|unk_0801341C|
		LDR r3, [pc, #0x1f0]
		CMP r2, #0xc8
		BLE      |sub_0801342C|
		MOV r2, #9
		LSL r2, r2, #6
		ADD r2, r3, r2
		LDR r2, [r2, #0x18]
		B        |loc_08013436|
