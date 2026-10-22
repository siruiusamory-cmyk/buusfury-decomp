	CODE16
|sub_08007A7A|
|unk_08007A7A|
		STRB r4, [r5, #4]
		LDR r0, [pc, #0xf0]
		MOV r4, #0
		MOV r7, #1
		LSL r7, r7, #0xb
		STR r0, [r5]
|loc_08007A86|
		LSL r0, r4, #2
		ADD r0, r0, r6
		LDR r0, [r0, #4]
		CMP r0, #0
		BNE      |loc_08007AA0|
		LSL r0, r4, #0xb
		ADD r0, r0, r5
		ADD r0, #8
		ADD r2, r7, #0
		MOV r1, #0
		BL       |sub_0804912C|
		B        |loc_08007AAA|
|loc_08007AA0|
		LSL r1, r4, #0xb
		ADD r1, r1, r5
|loc_08007AA4|
|unk_08007AA4|
		ADD r1, #8
		BL       |inc_0x03d784_0x041118| + 0x1bc
|loc_08007AAA|
		ADD r4, #1
		CMP r4, #2
		BLT      |loc_08007A86|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0x7920
