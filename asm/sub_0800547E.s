	CODE16
|sub_0800547E|
|unk_0800547E|
		ADD r5, r4, #0
		LDR r0, [pc, #0x264]
		MOV r6, #0
		STMIA r4!, {r0, r6}
		ADD r5, #0xff
		ADD r5, #1
		STR r6, [r5, #0xc]
		STR r6, [r5, #8]
		LDR r0, [pc, #0x25c]
		STR r6, [r5, #0x10]
		SUB r4, #8
		STR r0, [r4]
		ADD r0, r5, #0
		ADD r0, #0x2c
		BL       |sub_08004D38|
		LDR r0, [sp, #8]
		MOV r1, #0xff
		STR r0, [r5, #0x14]
		LDR r0, [sp, #0xc]
		ADD r1, #0x25
		STR r0, [r5, #0x18]
		STR r6, [r5, #0x28]
		STR r7, [r5, #0x20]
		MVN r0, r6
		STR r0, [r5, #0x1c]
		MOV r0, #6
		STRB r0, [r1, r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x5322
