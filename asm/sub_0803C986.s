	CODE16
|sub_0803C986|
|unk_0803C986|
		LDR r0, [sp, #0x4c]
		SUB r0, #4
		STR r0, [sp, #4]
		LDR r0, [sp, #0x44]
		STR r0, [sp, #0xc]
		B        |loc_0803C9A6|
|loc_0803C992|
|unk_0803C992|
		LDR r0, [sp, #0x50]
		STR r0, [sp, #8]
		LDR r0, [sp, #0x58]
		SUB r0, #6
		STR r0, [sp, #0x10]
		B        |loc_0803C9A6|
|loc_0803C99E|
|unk_0803C99E|
		LDR r0, [sp, #0x50]
		STR r0, [sp, #8]
		LDR r0, [sp, #0x38]
		STR r0, [sp, #0x10]
|loc_0803C9A6|
|unk_0803C9A6|
		STR r4, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		ADD r3, sp, #0
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x17c]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		STRB r7, [r3]
		STR r4, [sp, #0x30]
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r3, [r1, #0x24]
		ADD r3, r3, r1
		MOV r1, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		CMP r0, #0
		BEQ      |loc_0803C9F2|
		LDR r0, [pc, #0x160]
		LDR r4, [r0]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x154]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x150]
		ADD r3, r7, #0
		MOV r2, #0x40
		ADD r0, r4, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		B        |loc_0803C9F4|
|loc_0803C9F2|
|unk_0803C9F2|
		B        |loc_0803C9F4|
|loc_0803C9F4|
		ADD sp, #0x5c
		POP {r4, r5, r6, r7, pc}
		PUSH {r4, lr}
		ADD r4, r1, #0
		LDRH r1, [r1, #0x12]
		ADD r1, #1
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
		STRH r1, [r4, #0x12]
		CMP r1, #0x10
		BHS      |sub_0803CA10|
		MOV r2, #0
		STRB r2, [r4, #0x11]
		B        |inc_0x351c0_0x3d4d0| + 0x785a
