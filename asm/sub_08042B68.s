	CODE16
|sub_08042B68|
|unk_08042B68|
; cited by 0x080427E2 (a pc-relative load targets 0x08042BAC)
		BL       |loc_0804400c|
		CMP r0, #0
		BNE      |loc_08042B80|
		MOV r0, #2
		STRH r0, [r5, #0x14]
		MOV r1, #1
		MOV r0, #0xf3
		BL       |loc_0804333c|
		MOV r0, #2
		B        |inc_0x042118_0x049114| + 0xa4c
|loc_08042B80|
		ADD r1, r6, #0
		LDR r3, [pc, #0x38]
		MOV r0, #0
|loc_08042B86|
		LDRH r2, [r1]
		ADD r1, #2
		CMP r2, r3
		BEQ      |loc_08042B98|
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		CMP r0, #0x10
		BLO      |loc_08042B86|
|loc_08042B98|
		CMP r0, #0x10
		BNE      |loc_08042BC0|
		MOV r0, #4
		STRH r0, [r5, #0x14]
		MOV r1, #1
		MOV r0, #0xf3
		BL       |loc_0804333c|
		MOV r0, #4
		B        |inc_0x042118_0x049114| + 0xa4c
		DCD     0x0300525C
		DCD     0x03004CC8
		DCD     0x08042A4F
		DCD     0x080424B3
		DCD     0x0000FFFF
|loc_08042BC0|
		CMP r4, #1
		BLS      |loc_08042BCE|
		MOV r0, #1
		MOV r4, #1
		MOV r7, #0
		STRB r0, [r5, #7]
		B        |loc_08042BD6|
|loc_08042BCE|
		MOV r0, #0
		STRB r0, [r5, #7]
		CMP r4, #0
		BEQ      |loc_08042BDC|
|loc_08042BD6|
		MOV r0, #5
		STRB r0, [r5, #4]
		B        |loc_08042BEA|
|loc_08042BDC|
		MOV r0, #9
		STRB r0, [r5, #4]
		LDRB r0, [r5, #0xb]
		CMP r0, #0
		BEQ      |loc_08042BEA|
		MOV r0, #2
		STRB r0, [r5, #0xb]
|loc_08042BEA|
		STRB r4, [r5, #6]
		STRH r7, [r5, #0x1a]
		LDR r0, [sp, #0xc]
		STRH r0, [r5, #0x26]
		STR r6, [r5, #0x20]
		MOV r0, #0
		B        |inc_0x042118_0x049114| + 0xa4c
