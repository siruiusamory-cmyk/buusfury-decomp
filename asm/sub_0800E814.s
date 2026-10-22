	CODE16
|sub_0800E814|
|unk_0800E814|
		MOV r2, #0
		MVN r2, r2
		STR r2, [sp]
		ADD r2, r7, #0
		ADD r3, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xfc1c
		LDR r0, [pc, #0x30c]
		MOV r1, #1
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xc1
		STR r1, [r0, #0x10]
		STR r1, [r0, #0xc]
		MOV r1, #0
		STR r1, [r0, #8]
		STR r1, [r0, #0x14]
		STR r1, [r0, #0x18]
		STR r1, [r0, #0x1c]
		MOV r2, #1
		LSL r2, r2, #9
		STR r1, [r0, #0x20]
		STR r1, [r0, #0x24]
		ADD r2, r4, r2
		STR r1, [r2, #0x14]
		STR r1, [r2, #0x18]
		STR r1, [r2, #0x1c]
		STR r1, [r2, #0x20]
		STR r1, [r0, #0x34]
		STR r1, [r0, #0x30]
		STR r1, [r0, #0x38]
		STR r1, [r0, #0x3c]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xe6ba
