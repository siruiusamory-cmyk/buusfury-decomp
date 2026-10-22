	CODE16
|sub_0800FB56|
|unk_0800FB56|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0xc]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BNE      |loc_0800FB68|
		B        |inc_0x0158_0x143f2| + 0xf9fa
|loc_0800FB68|
		MOV r0, #1
		LSL r0, r0, #9
		ADD r0, r4, r0
		LDR r1, [r0, #0x24]
		LDR r0, [r4, #0x58]
		BL       |inc_0x1c3f2_0x2ab4c| + 0xb556
		ADD r3, r0, #1
		BNE      |loc_0800FB7E|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf9fa
|loc_0800FB7E|
		LDR r1, [r5]
		ADD r2, r1, #1
		LSL r3, r1, #2
		ADD r1, r3, r1
		LSL r1, r1, #3
		ADD r1, r1, r5
		STR r2, [r5]
		ADD r1, #4
		STR r0, [r1]
		MOV r0, #0xa3
		LSL r0, r0, #2
		ADD r0, r4, r0
		LDR r0, [r0]
		LDR r2, [pc, #0x14c]
		ADD r0, r0, r2
		ASR r0, r0, #0xa
		STR r0, [r1, #4]
		LDRB r0, [r4, #0x10]
		STR r0, [r1, #8]
		ADD r0, r1, #0
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0xa1
		LDMIA r1!, {r2}
		LDR r1, [r1]
		ASR r2, r2, #8
		ASR r1, r1, #8
		STR r1, [sp, #0x70]
		ADD r1, r2, #0
		STR r2, [sp, #0x6c]
		LDR r2, [sp, #0x70]
		STR r1, [sp, #0x74]
		STR r2, [sp, #0x78]
		LDR r1, [r7, #8]
		LDR r2, [sp, #0x74]
		ADD r1, #0x28
		LDR r3, [r1]
		ADD r0, #0xc
		SUB r2, r2, r3
		LDR r3, [sp, #0x78]
		LDR r1, [r1, #4]
		STR r2, [sp, #0x6c]
		SUB r1, r3, r1
		STR r1, [sp, #0x70]
		ADD r1, r2, #0
		LDR r2, [sp, #0x70]
		STMIA r0!, {r1, r2}
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf9fa
|loc_0800FBE0|
|unk_0800FBE0|
		B        |inc_0x0158_0x143f2| + 0xfa8e
|loc_0800FBE2|
|unk_0800FBE2|
		B        |inc_0x0158_0x143f2| + 0xfb36
|loc_0800FBE4|
|unk_0800FBE4|
		B        |inc_0x0158_0x143f2| + 0xfbd0
		LDRB r1, [r5]
		CMP r1, #1
		BEQ      |loc_0800FBF0|
		CMP r1, #2
		BNE      |inc_0x0158_0x143f2| + 0xfb32
|loc_0800FBF0|
		LDR r0, [r0, #0xc]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0xfb32
		ADD r6, r7, #0
		ADD r1, r4, #0
		ADD r0, sp, #0x6c
		BL       |loc_0800FE78|
		LDR r0, [r6]
		LDR r1, [sp, #0x74]
		CMP r0, r1
		BGE      |inc_0x0158_0x143f2| + 0xfb32
		LDR r0, [sp, #0x6c]
		LDR r1, [r6, #8]
		CMP r0, r1
		BGE      |inc_0x0158_0x143f2| + 0xfb32
		LDR r0, [r6, #4]
		LDR r1, [sp, #0x78]
		B        |loc_0800FC18|
