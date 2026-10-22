	CODE16
|sub_08024F52|
|unk_08024F52|
		ADD r0, r4, #0
		BL       |loc_08024A7C|
		LDR r0, [pc, #0x3ac]
		ADD r1, r4, #0
		STR r0, [r4]
		MOV r0, #0
		MOV r2, #0xed
		LSL r2, r2, #2
		ADD r1, #0x10
		ADD r2, r4, r2
		STR r0, [r4, #0x10]
		LDR r6, [pc, #0x3a0]
		STR r0, [r2]
|loc_08024F6E|
		LDR r3, [r6, #8]
		ASR r5, r0, #3
		ADD r3, r5, r3
		ADD r3, #0xc0
		LSL r7, r0, #0x1d
		LSR r7, r7, #0x1d
		LDRB r3, [r3, #5]
		MOV r5, #1
		LSL r5, r7
		AND r3, r5
		BEQ      |loc_08024F90|
		LDR r3, [r1]
		ADD r5, r3, #1
		LSL r3, r3, #2
		ADD r3, r3, r1
		STR r5, [r1]
		STR r0, [r3, #4]
|loc_08024F90|
		ADD r0, #1
		CMP r0, #0xe8
		BLT      |loc_08024F6E|
		LDR r5, [r4, #0x10]
		MOV r3, #0
		MOV r0, #0
		CMP r5, #0
		BLE      |loc_08024FD6|
		LDR r7, [pc, #0x36c]
|loc_08024FA2|
		LSL r5, r0, #2
		ADD r5, r5, r1
		LDR r5, [r5, #4]
		LSL r5, r5, #4
		ADD r5, r5, r7
		LDRH r5, [r5]
		CMP r3, r5
		BEQ      |loc_08024FC6|
		ADD r3, r5, #0
		LDR r5, [r2]
		ADD r6, r5, #1
		LSL r5, r5, #3
		ADD r5, r5, r2
		ADD r5, #4
		STR r6, [r2]
		STR r0, [r5]
		STR r0, [r5, #4]
		B        |loc_08024FCE|
|loc_08024FC6|
		LDR r5, [r2]
		LSL r5, r5, #3
		ADD r5, r5, r2
		STR r0, [r5]
|loc_08024FCE|
		LDR r5, [r4, #0x10]
		ADD r0, #1
		CMP r5, r0
		BGT      |loc_08024FA2|
|loc_08024FD6|
		MOV r0, #0x2b
		LSL r0, r0, #6
		ADD r0, r4, r0
		MOV r1, #0
		STR r1, [r0, #0x38]
		MOV r0, #0xb
		LSL r0, r0, #8
		ADD r0, r4, r0
		STR r1, [r0, #0xc]
		STRB r1, [r4, #0xe]
		STR r1, [r0, #0x10]
		STRB r1, [r4, #0xd]
		LDR r1, [r2]
		CMP r1, #0
		BEQ      |loc_08024FFA|
		LDR r1, [r2, #4]
		STR r1, [r0, #0x14]
		B        |loc_08025000|
|loc_08024FFA|
		MOV r1, #0
		MVN r1, r1
		STR r1, [r0, #0x14]
|loc_08025000|
		ADD r0, r4, #0
		DCW     0xE7A5
