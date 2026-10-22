	CODE16
|sub_08036BB2|
|unk_08036BB2|
		LDR r1, [pc, #0x1b8]
		LDR r3, [r0, #0x20]
		LDR r1, [r1, #4]
		ADD r2, r0, #0
		ADD r1, #0x18
		LDR r4, [r1]
		ADD r2, #0x18
		SUB r3, r3, r4
		LDR r4, [r0, #0x24]
		LDR r5, [r1, #4]
		STR r3, [sp]
		SUB r4, r4, r5
		STR r4, [sp, #4]
		STMIA r2!, {r3, r4}
		LDR r2, [r0, #0x20]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_08036BF2|
		LDR r2, [r1]
		LDR r3, [r0, #0x28]
		CMP r2, r3
		BGE      |loc_08036BF2|
		LDR r2, [r0, #0x24]
		LDR r3, [r1, #0xc]
		CMP r2, r3
		BGE      |loc_08036BF2|
		LDR r1, [r1, #4]
		LDR r0, [r0, #0x2c]
		CMP r1, r0
		BGE      |loc_08036BF2|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x19ec
|loc_08036BF2|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x19ec
