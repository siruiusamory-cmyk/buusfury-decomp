	CODE16
|sub_0803DD8A|
|unk_0803DD8A|
		ADD r5, r6, #0
		MOV r0, #0
		MOV r3, #0
|loc_0803DD90|
		LDRH r1, [r5]
		CMP r1, #0
		BEQ      |loc_0803DDD2|
		CMP r1, #0xa
		BNE      |loc_0803DD9E|
		ADD r5, #2
		B        |loc_0803DDD2|
|loc_0803DD9E|
		CMP r1, #8
		BNE      |loc_0803DDA6|
		ADD r5, #4
		B        |loc_0803DD90|
|loc_0803DDA6|
		CMP r1, #0x20
		BNE      |loc_0803DDAC|
		ADD r3, r5, #0
|loc_0803DDAC|
		LDR r2, [r4, #0xc]
		CMP r1, #0xff
		BLO      |loc_0803DDB8|
		LDR r1, [r2, #4]
		ADD r1, #1
		B        |loc_0803DDC4|
|loc_0803DDB8|
		LDR r2, [r2]
		LSL r1, r1, #1
		LDRH r1, [r2, r1]
		LSL r1, r1, #1
		LDRH r1, [r2, r1]
		ADD r1, #1
|loc_0803DDC4|
		ADD r0, r1, r0
		LDR r1, [sp, #0xc]
		CMP r0, r1
		BLE      |loc_0803DE02|
		CMP r3, #0
		BEQ      |loc_0803DDD2|
		ADD r5, r3, #0
|loc_0803DDD2|
		SUB r0, r5, r6
		ASR r7, r0, #1
		BEQ      |loc_0803DE38|
		LDR r0, [sp, #4]
		LDR r1, [r4, #0x14]
		SUB r1, #0x10
		CMP r0, r1
		BLE      |loc_0803DE38|
		ADD r2, r7, #0
		ADD r1, r6, #0
		LDR r0, [r4, #0xc]
		BL       |loc_0804001A|
		LDRB r1, [r4]
		CMP r1, #0
		BEQ      |loc_0803DE06|
		CMP r1, #1
		BEQ      |loc_0803DE0C|
		CMP r1, #2
		BNE      |loc_0803DE16|
		LDR r1, [r4, #4]
		SUB r0, r1, r0
		STR r0, [sp]
		B        |loc_0803DE16|
|loc_0803DE02|
		ADD r5, #2
		B        |loc_0803DD90|
|loc_0803DE06|
		LDR r0, [r4, #4]
		STR r0, [sp]
		B        |loc_0803DE16|
|loc_0803DE0C|
		ADD r0, #1
		LDR r1, [r4, #4]
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [sp]
|loc_0803DE16|
		LDRH r1, [r6]
		ADD r6, #2
		CMP r1, #8
		BNE      |loc_0803DE28|
		LDRH r0, [r6]
		ADD r6, #2
		SUB r7, #1
		STRB r0, [r4, #3]
		B        |loc_0803DE32|
|loc_0803DE28|
		MOV r2, sp
		ADD r0, r4, #0
		LDR r3, [r4, #0x20]
		BL       |inc_0x046118_0x049114| + 0x98e
|loc_0803DE32|
		SUB r7, #1
		CMP r7, #0
		BGT      |loc_0803DE16|
|loc_0803DE38|
		LDRB r1, [r4, #1]
		LDR r0, [sp, #4]
		ADD r0, r0, r1
		STR r0, [sp, #4]
		LDRB r1, [r4, #1]
		LDR r0, [r4, #8]
		ADD r0, r0, r1
		STR r0, [r4, #8]
		ADD r6, r5, #0
		B        |inc_0x03d784_0x041118| + 0x5f0
|loc_0803DE4C|
|unk_0803DE4C|
		ADD sp, #0x14
		POP {r4, r5, r6, r7, pc}
