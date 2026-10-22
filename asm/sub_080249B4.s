	CODE16
|sub_080249B4|
|unk_080249B4|
		ADD r3, #0xff
		LSL r0, r3, #0x18
		LSR r0, r0, #0x18
		STRB r0, [r4]
		BNE      |loc_080249D6|
		LDRH r0, [r4, #2]
		LDR r1, [pc, #0x64]
		CMP r0, r1
		BEQ      |loc_080249D6|
		MOV r3, #2
		LDRSH r1, [r4, r3]
		LDR r0, [r5]
		BL       |loc_0801142A|
		MOV r0, #0
		MVN r0, r0
		STRH r0, [r4, #2]
|loc_080249D6|
		MOV r0, #0
		DCW     0xE7EB
|loc_080249DA|
|unk_080249DA|
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7E8
