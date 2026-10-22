	CODE16
|sub_080141A0|
|unk_080141A0|
		LDR r0, [pc, #0x26c]
		ADD r1, r5, #0
		STR r0, [r5]
		MOV r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r0, [r5, #4]
		STR r0, [r1, #0xc]
		STR r0, [r1, #8]
		LDR r2, [pc, #0x260]
		STR r0, [r1, #0x10]
		STR r2, [r5]
		ADD r2, r1, #0
		ADD r2, #0x2c
		STR r2, [sp, #0x70]
		STR r0, [r2]
		ADD r2, #0xa4
		STR r2, [sp, #0x6c]
		STR r0, [r2]
		STR r0, [r1, #0x1c]
		STR r0, [r1, #0x28]
		MOV r4, #0
		LDR r6, [pc, #0x248]
		MOV r7, #0x9d
		LSL r7, r7, #2
		STR r0, [sp]
		STR r0, [sp, #0x44]
|loc_080141D6|
		LSL r0, r4, #8
		ADD r0, r0, r5
		ADD r1, r0, r7
		LSL r0, r4, #2
		LDR r0, [r6, r0]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		ADD r4, #1
		CMP r4, #3
		BLT      |loc_080141D6|
		MOV r6, #0
		MOV r7, sp
|loc_080141EE|
		LDR r1, [pc, #0x22c]
		LSL r0, r6, #4
		ADD r4, r0, r1
		MOV r2, #0
		ADD r0, r7, #0
		LDR r1, [r4, #4]
		BL       |loc_08004038|
		LDR r0, [sp, #4]
		CMP r0, #0
		BNE      |loc_08014252|
		MOV r2, #0
		ADD r0, r7, #0
		LDR r1, [r4, #8]
		BL       |loc_08004038|
		LDR r0, [sp, #4]
		CMP r0, #0
		BEQ      |loc_0801422C|
		LDR r2, [sp, #0x6c]
		LDR r0, [r2]
		ADD r1, r0, #1
		STR r1, [r2]
		LDRB r1, [r4]
		LSL r0, r0, #2
		ADD r0, r0, r2
		ADD r0, #4
		STRB r1, [r0]
		LDRH r1, [r4, #2]
		STRH r1, [r0, #2]
		B        |loc_08014252|
|loc_0801422C|
		MOV r2, #0
		ADD r0, r7, #0
		LDR r1, [r4, #0xc]
		BL       |loc_08004038|
		LDR r0, [sp, #4]
		CMP r0, #0
		BEQ      |loc_08014252|
		LDR r2, [sp, #0x70]
		LDR r0, [r2]
		ADD r1, r0, #1
		STR r1, [r2]
		LDRB r1, [r4]
		LSL r0, r0, #2
		ADD r0, r0, r2
		ADD r0, #4
		STRB r1, [r0]
		LDRH r1, [r4, #2]
		STRH r1, [r0, #2]
|loc_08014252|
		ADD r6, #1
		CMP r6, #0x28
		BLT      |loc_080141EE|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0x14044
		PUSH {r4, r5, r6, lr}
		SUB sp, #0x20
		MOV r2, #0
		STR r2, [sp, #0xc]
		MOV r1, #1
		MOV r2, #0x84
		STR r2, [sp]
		STR r1, [sp, #4]
		STR r1, [sp, #8]
		ADD r4, r0, #0
		ADD r1, r4, #0
		MOV r2, #1
		MOV r3, #0xc
		MOV r0, #0
		BL       |loc_08013E64|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		LDR r5, [pc, #0x198]
		LDR r0, [pc, #0x190]
		LDR r3, [r5, #0x68]
		SUB r0, #0xc
		LDR r2, [r0, #8]
		MOV r1, #0
		STR r1, [sp, #8]
		STR r3, [sp]
		MOV r0, #5
		STR r2, [sp, #0xc]
		MOV r2, #0x1c
		STR r0, [sp, #4]
		MOV r3, #0x90
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		MOV r2, #0
		STR r2, [sp, #0xc]
		MOV r2, #8
		MOV r1, #1
		STR r1, [sp, #8]
		STR r2, [sp]
		MOV r0, #6
		STR r0, [sp, #4]
		MOV r2, #6
		ADD r1, r4, #0
		MOV r3, #8
		MOV r0, #0
		BL       |loc_08013E64|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		MOV r2, #0
		STR r2, [sp, #0xc]
		MOV r2, #8
		MOV r1, #1
		STR r1, [sp, #8]
		STR r2, [sp]
		MOV r0, #7
		STR r0, [sp, #4]
		MOV r2, #7
		ADD r1, r4, #0
		MOV r3, #0xd0
		MOV r0, #0
		BL       |loc_08013E64|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		LDR r0, [pc, #0x120]
		LDR r3, [r5, #8]
		SUB r0, #0xc
		LDR r2, [r0, #8]
		STR r3, [sp]
		MOV r1, #0
		MOV r6, #0x14
		ADD r3, r6, #0
		STR r1, [sp, #8]
		MOV r0, #2
		STR r2, [sp, #0xc]
		MOV r2, #0x22
		STR r0, [sp, #4]
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		LDR r0, [pc, #0xf4]
		LDR r3, [r5, #0x70]
		SUB r0, #0xc
		LDR r2, [r0, #8]
		MOV r1, #2
		STR r3, [sp]
		ADD r3, r6, #0
		STR r1, [sp, #4]
		STR r1, [sp, #8]
		STR r2, [sp, #0xc]
		MOV r2, #0xce
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		MOV r2, #0
		STR r2, [sp, #0xc]
		MOV r2, #0x28
		MOV r1, #1
		MOV r6, #0xd4
		ADD r3, r6, #0
		STR r1, [sp, #8]
		STR r2, [sp]
		MOV r0, #2
		STR r0, [sp, #4]
		MOV r2, #2
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08013E64|
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #1
		STR r0, [r5, #0x20]
		MOV r2, #0
		STR r2, [sp, #0xc]
		MOV r2, #0x70
		MOV r1, #1
		STR r1, [sp, #8]
		STR r2, [sp]
		MOV r0, #3
		ADD r3, r6, #0
		ADD r1, r4, #0
		STR r0, [sp, #4]
		MOV r2, #3
		MOV r0, #0
		BL       |loc_08013E64|
		STR r0, [r5, #0x24]
		LDR r1, [r5, #0x20]
		ADD r0, r4, #0
		BL       |loc_0800664E|
		ADD r0, r4, #0
		LDR r1, [r5, #0x24]
		BL       |loc_0800664E|
		MOV r2, #0
		MOV r6, #0
		MVN r6, r6
		STR r2, [sp, #0x1c]
		MOV r2, #0x18
		STR r2, [sp, #0x10]
		MOV r1, #1
		STR r1, [sp, #0x18]
		ADD r2, r6, #0
		MOV r1, #0x1f
		STR r1, [sp, #0xc]
		ADD r3, r6, #0
		MOV r0, #0x20
		STR r0, [sp, #0x14]
		ADD r1, r4, #0
		MOV r0, #0
		STR r2, [sp]
		STR r2, [sp, #4]
		STR r6, [sp, #8]
		BL       |loc_08015C62|
		ADD r1, r0, #0
		STR r0, [r5, #0x14]
		ADD r0, r4, #0
		BL       |loc_0800664E|
		LDR r0, [r5, #0x14]
		MOV r2, #1
		LDR r1, [r0, #0x28]
		LDR r0, [r0, #0x20]
		STR r2, [sp, #0x1c]
		SUB r3, r1, r0
		MOV r0, #0x20
		STR r0, [sp, #0x14]
		NEG r0, r2
		MOV r1, #0
		STR r1, [sp, #0x18]
		ADD r2, r0, #0
		ADD r3, #0x1c
		STR r3, [sp, #0x10]
		MOV r1, #0x20
		STR r1, [sp, #0xc]
		ADD r3, r6, #0
		ADD r1, r4, #0