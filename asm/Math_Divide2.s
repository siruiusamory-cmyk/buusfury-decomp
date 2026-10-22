|Math_Divide2|
	CODE16
|unk_0800CBB8|
		LDR r0, [pc, #0x218]
		LDR r2, [r4, #0x44]
		LDR r1, [r0, #4]
		ADD r1, #0x18
		LDR r3, [r1]
		CMP r2, r3
		BLT      |loc_0800CBDA|
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0800CBDA|
		LDR r2, [r4, #0x48]
		LDR r3, [r1, #4]
		CMP r2, r3
		BLT      |loc_0800CBDA|
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BLT      |loc_0800CBDE|
|loc_0800CBDA|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xca5c
|loc_0800CBDE|
		LDR r2, [r4, #0x44]
		ADD r1, sp, #0x14
		LSL r2, r2, #0xa
		STR r2, [sp, #0x14]
		LDR r2, [r4, #0x48]
		ADD r3, sp, #4
		LSL r2, r2, #0xa
		STR r2, [sp, #0x18]
		LDR r2, [r4, #0x54]
		STR r2, [sp, #0x1c]
		ADD r2, sp, #0x10
		LDR r0, [r0, #4]
		STR r2, [sp]
		ADD r2, sp, #0xc
		BL       |sub_0802f1c6|
		LDR r0, [sp, #0xc]
		CMP r0, #0
		BNE      |loc_0800CC06|
		B        |inc_0x0158_0x143f2| + 0xca5c
|loc_0800CC06|
		LDR r0, [sp, #0x10]
		LSL r3, r0, #2
		ADD r0, r3, r0
		LSL r0, r0, #1
		ASR r0, r0, #0xc
		STR r0, [r4, #0x58]
		CMP r0, #0x80
		BGE      |loc_0800CC1A|
		MOV r0, #0x80
		STR r0, [r4, #0x58]
|loc_0800CC1A|
		LDR r0, [r4, #0x3c]
		LDR r1, [r4, #0x58]
		SWI 6
		LDR r1, [sp, #4]
		SUB r0, r1, r0
		LDR r1, [r4, #0x34]
		SUB r0, r0, r1
		STR r0, [r4, #0x4c]
		CMP r0, #0xf0
		BLT      |loc_0800CC32|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xca5c
|loc_0800CC32|
		LSL r1, r1, #1
		NEG r1, r1
		CMP r0, r1
		BGE      |loc_0800CC3E|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xca5c
|loc_0800CC3E|
		LDR r0, [r4, #0x40]
		LDR r1, [r4, #0x58]
		SWI 6
		LDR r1, [sp, #8]
		SUB r0, r1, r0
		LDR r1, [r4, #0x38]
		SUB r0, r0, r1
		STR r0, [r4, #0x50]
		CMP r0, #0xa0
		BLT      |loc_0800CC56|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xca5c
|loc_0800CC56|
		LSL r1, r1, #1
		NEG r1, r1
		CMP r0, r1
		BGE      |loc_0800CC62|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xca5c
|loc_0800CC62|
		LDR r0, [sp, #0x10]
		NEG r0, r0
		STR r0, [r4, #4]
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0xca5c
