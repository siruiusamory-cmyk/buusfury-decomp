	CODE16
|sub_0801170A|
|unk_0801170A|
		LDRB r3, [r0]
		MOV r1, #0
		CMP r3, #0xff
		BEQ      |loc_0801172E|
		LDR r2, [pc, #0xfc]
|loc_08011714|
		ADD r4, r3, #0
		LSL r3, r4, #2
		ADD r3, r3, r4
		LSL r3, r3, #1
		ADD r3, r3, r0
		ADD r3, r3, r2
		LDRH r4, [r3, #4]
		CMP r4, r1
		BLE      |loc_08011728|
		ADD r1, r4, #0
|loc_08011728|
		LDRB r3, [r3, #8]
		CMP r3, #0xff
		BNE      |loc_08011714|
|loc_0801172E|
		LSL r0, r1, #6
		B        |inc_0x0158_0x143f2| + 0x115ae
