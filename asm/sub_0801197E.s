	CODE16
|sub_0801197E|
|unk_0801197E|
		LDR r1, [pc, #0x11c]
		ADD r5, r5, r1
		LDR r3, [r5]
		MOV r1, #0
		CMP r3, #0
		BLE      |inc_0x0158_0x143f2| + 0x11846
|loc_0801198A|
|unk_0801198A|
		LSL r2, r1, #2
		ADD r2, r2, r5
		LDR r2, [r2, #4]
		CMP r2, r4
		BNE      |sub_08011998|
		ADD r0, r1, #0
		B        |inc_0x0158_0x143f2| + 0x11846
