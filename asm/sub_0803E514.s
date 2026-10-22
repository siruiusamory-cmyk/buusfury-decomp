	CODE16
|sub_0803E514|
|unk_0803E514|
		LDRB r5, [r2, #0xc]
		LSL r4, r4, #2
		LSL r3, r3, #0x1a
		STRB r5, [r1, #8]
		LDR r5, [pc, #0x288]
		LDR r4, [r5, r4]
		STR r4, [r0, #0x40]
		STRB r6, [r1, #0xa]
		BPL      |loc_0803E536|
		LDRB r1, [r1, #8]
		STR r4, [r0, #0x30]
		MOV r2, #0x17
		STRB r1, [r0, #0x12]
		LDRB r1, [r0, #0x10]
		ORR r1, r2
		STRB r1, [r0, #0x10]
		DCW     0xE7EC
|loc_0803E536|
		LDR r3, [pc, #0x270]
		LDRB r2, [r2, #0xb]
		SUB r3, #4
		LDR r3, [r3]
		LDRB r1, [r1, #8]
		LDR r3, [r3, #0xc]
		LDR r5, [r3, #8]
		LSL r3, r2, #1
		ADD r2, r3, r2
		LSL r2, r2, #2
		ADD r2, r5, r2
		STR r2, [r0, #0x28]
		STR r4, [r0, #0x30]
		STRB r1, [r0, #0x12]
		LDRB r1, [r0, #0x10]
		MOV r2, #0x1f
		ORR r1, r2
		STRB r1, [r0, #0x10]
		DCW     0xE7D9
|loc_0803E55C|
|unk_0803E55C|
		MOV r4, #0x44
		AND r3, r4
		DCW     0xD0D6
		LDRB r3, [r2, #0xc]
		STRB r3, [r1, #8]
		LDRB r1, [r2, #0xc]
		MOV r2, #0x10
		STRB r1, [r0, #0x12]
		LDRB r1, [r0, #0x10]
		ORR r1, r2
		STRB r1, [r0, #0x10]
		DCW     0xE7CD
