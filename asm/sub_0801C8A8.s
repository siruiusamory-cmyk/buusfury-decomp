	CODE16
|sub_0801C8A8|
|unk_0801C8A8|
		LDR r1, [r4, #0x20]
		LDR r2, [r4, #0x40]
		ADD r1, r1, r2
		STR r1, [r4, #0x20]
		LDR r0, [r4, #0x44]
		LDR r1, [r4, #0x24]
		ADD r0, r1, r0
		STR r0, [r4, #0x24]
		LDR r0, [r4, #0x44]
		ADD r0, #0x20
		STR r0, [r4, #0x44]
		B        |loc_0801C82C|
|loc_0801C8C0|
|unk_0801C8C0|
		LDR r1, [r4, #0x50]
		SUB r1, #0x20
		STR r1, [r4, #0x50]
		LDR r2, [r4, #0x4c]
		ADD r1, r2, r1
		LDR r2, [pc, #0x30]
		STR r1, [r4, #0x4c]
		CMP r1, r2
		BGE      |loc_0801C8A4|
		STRB r0, [r5, #4]
		MOV r0, #0x1e
		ADD r4, #0x58
		STMIA r4!, {r0, r6}
		B        |loc_0801C8A4|
