	CODE16
|sub_080119EA|
|unk_080119EA|
		LDR r2, [pc, #0xb0]
		ADD r0, r0, r2
		LDR r6, [r0]
		MOV r2, #0
		CMP r6, #0
		BLE      |loc_08011A06|
|loc_080119F6|
		LSL r3, r2, #2
		ADD r3, r3, r0
		LDR r3, [r3, #4]
		CMP r3, r1
		BEQ      |loc_08011A0A|
		ADD r2, #1
		CMP r6, r2
		BGT      |loc_080119F6|
|loc_08011A06|
		MOV r2, #0
		MVN r2, r2
|loc_08011A0A|
		ADD r1, r2, #0
		BL       |inc_0x049120_0x055620| + 0x6d34
		LDR r0, [r4]
		ADD r1, r0, #1
		LSL r0, r0, #2
		ADD r0, r0, r4
		STR r1, [r4]
		STR r5, [r0, #4]
		B        |inc_0x0158_0x143f2| + 0x11890
