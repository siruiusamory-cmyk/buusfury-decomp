	CODE16
|sub_080061CA|
|unk_080061CA|
		MOV r0, #0x2c
		LDRB r1, [r0, r4]
		CMP r1, #0
		BEQ      |loc_080061F4|
		LDR r0, [pc, #0xb4]
		CMP r1, #1
		BEQ      |loc_080061FA|
		CMP r1, #2
		BNE      |loc_080061EA|
		LDR r1, [r4, #0x1c]
		LDR r0, [r0, #4]
		BL       |sub_0803FFE8|
		LDR r1, [r4, #0x20]
		SUB r0, r1, r0
		STR r0, [r5]
|loc_080061EA|
		LDR r0, [r4, #0x24]
		SUB r0, #4
		STR r0, [r5, #4]
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x6070
|loc_080061F4|
		LDR r0, [r4, #0x20]
		STR r0, [r5]
		B        |loc_080061EA|
|loc_080061FA|
		LDR r1, [r4, #0x1c]
		LDR r0, [r0, #4]
		BL       |sub_0803FFE8|
		LDR r1, [r4, #0x20]
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [r5]
		B        |loc_080061EA|
		ADD r2, r0, #0
		ADD r0, r1, #0
		MOV r1, #1
		PUSH {r4, lr}
		STRB r1, [r0]
		STRB r1, [r0, #2]
		LDR r1, [pc, #0x70]
		STR r1, [r0, #0x20]
		LDR r1, [r2, #4]
		ADD r1, #0xff
		ADD r1, #1
		LDR r1, [r1, #0xc]
		LDR r3, [r2, #8]
		CMP r1, r3
		BNE      |sub_0800622E|
		MOV r1, #6
		B        |inc_0x0158_0x143f2| + 0x60d8
