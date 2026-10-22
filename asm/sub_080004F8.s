	CODE16
|sub_080004F8|
|unk_080004F8|
		LSL r3, r3, #0x1f
		BEQ      |loc_0800050A|
		ADD r1, #0x1e
		LDRH r1, [r1]
		STR r2, [r0]
		LSL r2, r4, #2
		ADD r0, r2, r0
		STR r1, [r0, #4]
		B        |inc_0x0158_0x143f2| + 0x39c
|loc_0800050A|
		ADD r1, #0x1a
		MOV r3, #0
		LDRSH r1, [r1, r3]
		STR r2, [r0]
		LSL r2, r4, #2
		ADD r0, r2, r0
		STR r1, [r0, #4]
		B        |inc_0x0158_0x143f2| + 0x39c
