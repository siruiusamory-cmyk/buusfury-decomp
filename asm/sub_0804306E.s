	CODE16
|sub_0804306E|
|unk_0804306E|
		ADD r2, r1, #0
		MOV r1, #5
		CMP r2, #2
		BNE      |loc_08043080|
		MOV r2, #3
		STRB r2, [r0, #7]
		MOV r2, #9
		STRB r2, [r0, #4]
		B        |loc_08043086|
|loc_08043080|
		MOV r2, #1
		STRB r2, [r0, #7]
		STRB r1, [r0, #4]
|loc_08043086|
		LDRB r2, [r0]
		CMP r2, #0
		BEQ      |loc_0804306C|
		MOV r2, #0
		STRH r2, [r0, #0x1a]
		MOV r2, #8
		STRB r2, [r0, #7]
		STRB r1, [r0, #4]
		B        |loc_0804306C|
