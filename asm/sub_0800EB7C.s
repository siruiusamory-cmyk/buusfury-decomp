	CODE16
|sub_0800EB7C|
|unk_0800EB7C|
		LDRH r5, [r6, #2]
		LDR r0, [pc, #0x25c]
		LDR r7, [pc, #0x25c]
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		LDR r0, [r7]
		ADD r1, r5, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0800EBA2|
		ADD r1, r5, #0
		LDR r0, [r7]
		BL       |sub_08011732|
		ADD r1, r5, #0
		LDR r0, [r7]
		BL       |loc_0801124C|
|loc_0800EBA2|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x23c]
		MOV r7, #0
		STR r0, [r4]
		LDR r0, [sp, #8]
		ADD r5, r4, #0
		STR r0, [r4, #0x14]
		STR r6, [r4, #0x58]
		STR r7, [r4, #0x24]
		STR r7, [r4, #0x4c]
		LDR r0, [r6, #0x50]
		ADD r5, #0xff
		ADD r5, #0x81
		CMP r0, #0
		BEQ      |loc_0800EBD0|
		LDR r0, [r0]
		LDR r1, [pc, #0x21c]
		MOV r2, #0x80
		STR r0, [r4, #0x4c]
		LDR r0, [pc, #0x21c]
		ADD r1, #8
		BL       |loc_0804E490|
|loc_0800EBD0|
		LDR r0, [r6, #0x54]
		STR r0, [r4, #0x50]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0x75
		STRH r7, [r0]
		STRH r7, [r0, #2]
		LDR r0, [pc, #0x208]
		STR r7, [r5]
		SUB r0, #4
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		ADD r0, #0xff
		STR r7, [r4, #0x30]
		STR r7, [r4, #0x38]
		ADD r0, #0x79
		STR r7, [r0]
		STR r7, [r0, #4]
		LDR r0, [r4, #0x58]
		LDR r1, [r0, #4]
		STR r1, [r4, #0x34]
		LDR r1, [r0, #4]
		STR r1, [r4, #0x3c]
		STRB r7, [r4, #0x10]
		LDRH r0, [r0, #2]
		DCW     0xF02E
		DCW     0xFCD9
		STR r0, [r4, #0x40]
		LDR r0, [r4, #0x58]
		LDRB r1, [r0, #0xb]
		LDRB r0, [r0, #0xa]
		BL       |loc_08013E38|
		STR r0, [r4, #0x5c]
		CMP r0, #0
		BEQ      |loc_0800EC22|
		LDRH r2, [r0, #2]
		LDR r1, [r0, #4]
		LDR r0, [r0, #8]
		BL       |loc_0804E490|
|loc_0800EC22|
		LDR r0, [r4, #0x14]
		LDR r1, [r0]
		LDR r2, [r1]
		ADD r2, r2, r1
		ADD r1, r4, #0
		BL       |Thunk_JumpRegister1|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xea20
