	CODE16
|sub_080102FC|
|unk_080102FC|
		MOV r0, #0xff
		ADD r0, #0x99
		LDR r0, [r0, r4]
		CMP r0, r5
		BNE      |loc_0801030A|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x101a0
|loc_0801030A|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x101a0
|loc_0801030E|
|unk_0801030E|
		MOV r1, #0
		LDR r0, [r4, #0x58]
		BL       |inc_0x1c3f2_0x2ab4c| + 0xb556
		ADD r3, r0, #1
		BNE      |loc_0801031E|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x101a0
|loc_0801031E|
		LDR r1, [r5]
		ADD r2, r1, #1
		LSL r3, r1, #2
		ADD r1, r3, r1
		LSL r1, r1, #3
		ADD r1, r1, r5
		ADD r1, #4
		STR r2, [r5]
		STR r0, [r1]
		MOV r0, #0
		MVN r0, r0
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
		STR r1, [sp, #8]
		ADD r1, r2, #0
		STR r2, [sp, #4]
		LDR r2, [sp, #8]
		STR r1, [sp, #0xc]
		LDR r1, [pc, #0x2c]
		STR r2, [sp, #0x10]
		LDR r1, [r1]
		LDR r2, [sp, #0xc]
		ADD r1, #0x28
		LDR r3, [r1]
		ADD r0, #0xc
		SUB r2, r2, r3
		LDR r3, [sp, #0x10]
		LDR r1, [r1, #4]
		STR r2, [sp, #4]
		SUB r1, r3, r1
		STR r1, [sp, #8]
		ADD r1, r2, #0
		LDR r2, [sp, #8]
		STMIA r0!, {r1, r2}
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x101a0
|loc_08010378|
|unk_08010378|
		ADD r2, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xf46e
		B        |inc_0x0158_0x143f2| + 0x101a0
