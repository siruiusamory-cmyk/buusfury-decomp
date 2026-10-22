	CODE16
|sub_0801FBDC|
|unk_0801FBDC|
		LDRB r7, [r2, #4]
		CMP r7, #0
		BNE      |loc_0801FBE6|
		MVN r0, r7
		B        |loc_0801FC0C|
|loc_0801FBE6|
		LDR r6, [r1]
		MOV r0, #0
		CMP r6, #0
		BLE      |loc_0801FC08|
|loc_0801FBEE|
		LSL r4, r0, #3
		ADD r4, r4, r1
		ADD r4, #4
		LDRB r5, [r4, #4]
		CMP r5, r7
		BNE      |loc_0801FC02|
		LDRB r4, [r4, #5]
		LDRB r5, [r2, #5]
		CMP r4, r5
		BEQ      |loc_0801FC0C|
|loc_0801FC02|
		ADD r0, #1
		CMP r6, r0
		BGT      |loc_0801FBEE|
|loc_0801FC08|
		MOV r0, #0
		MVN r0, r0
|loc_0801FC0C|
		CMP r0, #0
		BLT      |loc_0801FC20|
		LSL r0, r0, #3
		ADD r0, r0, r1
		ADD r0, #4
		LDR r1, [r0]
		ADD r1, r1, r3
		STR r1, [r0]
		MOV r0, #1
		DCW     0xE7DB
|loc_0801FC20|
		LDR r0, [r1]
		CMP r0, #5
		BNE      |loc_0801FC2A|
		MOV r0, #0
		DCW     0xE7D6
|loc_0801FC2A|
		ADD r4, r0, #1
		LSL r0, r0, #3
		ADD r0, r0, r1
		STR r4, [r1]
		LDR r1, [r2, #4]
		ADD r0, #4
		STR r1, [r0, #4]
		STR r3, [r0]
		MOV r0, #1
		DCW     0xE7CC
