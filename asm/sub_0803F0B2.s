	CODE16
|sub_0803F0B2|
|unk_0803F0B2|
		CMP r0, #0
		BEQ      |loc_0803F0DA|
		STR r0, [sp]
		MOV r5, #0
|loc_0803F0BA|
		LSL r0, r5, #1
		ADD r0, r0, r5
		LSL r0, r0, #5
		ADD r0, r0, r4
		ADD r0, #0x18
		ADD r1, r6, #0
		LDR r2, [sp]
		BL       |loc_0803E152|
		ADD r5, #1
		CMP r5, #0xf
		BLT      |loc_0803F0BA|
		LDRH r0, [r4, #8]
		LSL r1, r0, #2
		ADD r6, r1, r6
		SUB r7, r7, r0
|loc_0803F0DA|
		ADD r0, r4, #0
		BL       |sub_0803EFD0|
		LDRH r0, [r4, #6]
		STRH r0, [r4, #8]
		DCW     0xE7D1
