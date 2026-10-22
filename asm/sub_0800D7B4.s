	CODE16
|sub_0800D7B4|
|unk_0800D7B4|
		LDR r1, [r4, #0x4c]
		CMP r1, #0
		BEQ      |loc_0800D7EA|
		ADD r7, r1, #4
		LDMIA r7!, {r2, r7}
		STR r2, [sp, #4]
		LDRH r1, [r1, #2]
		STR r1, [sp, #8]
		LDRB r1, [r7]
		ADD r2, r1, #1
		STRB r2, [r7]
		CMP r1, #0
		BNE      |loc_0800D7EA|
		LDR r1, [sp, #8]
		LDR r0, [r0]
		BL       |loc_0801124C|
		LSL r0, r0, #0x10
		ASR r0, r0, #0x10
		STRH r0, [r7, #2]
		LDR r1, [pc, #0xac]
		LSL r0, r0, #5
		ADD r0, r0, r1
		ADD r2, sp, #4
		LDMIA r2!, {r1, r2}
		BL       |Thunk_VramCopy|
|loc_0800D7EA|
		ADD r2, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xd9fa
		B        |loc_0800D7B0|
|loc_0800D7F6|
|unk_0800D7F6|
		LDR r1, [r4, #0x4c]
		CMP r1, #0
		BEQ      |loc_0800D822|
		LDR r7, [r1, #8]
		LDRB r1, [r7]
		ADD r1, #0xff
		LSL r1, r1, #0x18
		LSR r1, r1, #0x18
		STRB r1, [r7]
		BNE      |loc_0800D822|
		LDRH r1, [r7, #2]
		LDR r2, [pc, #0x80]
		CMP r1, r2
		BEQ      |loc_0800D822|
		MOV r3, #2
		LDRSH r1, [r7, r3]
		LDR r0, [r0]
		BL       |loc_0801142A|
		MOV r0, #0
		MVN r0, r0
		STRH r0, [r7, #2]
|loc_0800D822|
		ADD r2, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xd9fa
		B        |loc_0800D7B0|
|loc_0800D82E|
|unk_0800D82E|
		LDR r0, [r4, #0x44]
		CMP r0, #0
		BNE      |loc_0800D866|
		LDR r0, [r4, #0x18]
		LDR r1, [r5, #8]
		CMP r0, r1
		BGE      |loc_0800D866|
		LDR r0, [r5]
		LDR r1, [r4, #0x20]
		CMP r0, r1
		BGE      |loc_0800D866|
		LDR r0, [r4, #0x1c]
		LDR r1, [r5, #0xc]
		CMP r0, r1
		BGE      |loc_0800D866|
		LDR r0, [r5, #4]
		LDR r1, [r4, #0x24]
		CMP r0, r1
		BGE      |loc_0800D866|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		LDR r1, [r5, #0x10]
		BL       |Thunk_JumpRegister1|
		MOV r0, #1
		B        |loc_0800D7B0|
|loc_0800D866|
		MOV r0, #0
		B        |loc_0800D7B0|
|loc_0800D86A|
|unk_0800D86A|
; cited by 0x0800D5AA (a pc-relative load targets 0x0800D878)
		ADD r2, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xd9fa
		B        |loc_0800D7B0|
	INCBIN  baserom.gba_0xd876_0xd892.extracted
