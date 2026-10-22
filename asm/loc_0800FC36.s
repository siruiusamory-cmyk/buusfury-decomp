	CODE16
|loc_0800FC36|
|unk_0800FC36|
; cited by 0x0800F938 (a pc-relative load targets 0x0800FCE0)
		B        |loc_0800FD08|
|unk_0800FC38|
		LDR r1, [r5, #0x2c]
		CMP r1, #0
		BEQ      |loc_0800FC62|
		LDR r1, [r5, #0x1c]
		ADD r2, sp, #0x6c
		LDRB r1, [r1]
		STR r1, [sp, #0x6c]
		LDR r1, [r5, #0x1c]
		LDRB r1, [r1, #1]
		STR r1, [sp, #0x70]
		LDR r0, [r0]
		LDR r1, [pc, #0x98]
		ADD r0, r0, r1
		ASR r0, r0, #0xa
		STR r0, [sp, #0x74]
		LDR r0, [r5, #0x24]
		LDR r1, [pc, #0x90]
		STR r0, [sp, #0x78]
		MOV r0, sp
		BL       |loc_08004098|
|loc_0800FC62|
		MOV r0, #5
		LSL r0, r0, #7
		LDR r1, [r5, #0x24]
		ADD r0, r4, r0
		STR r1, [r0, #0x14]
		LDR r2, [r5, #0x1c]
		MOV r1, #1
		LDRB r2, [r2, #1]
		CMP r2, #3
		BEQ      |loc_0800FC78|
		MOV r1, #0
|loc_0800FC78|
		STR r1, [r0, #0x18]
		MOV r0, #0x47
		LSL r0, r0, #3
		ADD r1, r6, #0
		ADD r0, r4, r0
		BL       |inc_0x0158_0x143f2| + 0xa9d6
		MOV r0, #1
|loc_0800FC88|
		B        |inc_0x0158_0x143f2| + 0xf9fa
|unk_0800FC8A|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf9fa
		LDRB r1, [r5]
		CMP r1, #1
		BEQ      |loc_0800FC98|
		CMP r1, #2
		BNE      |loc_0800FCFC|
|loc_0800FC98|
		LDR r0, [r0, #0xc]
		CMP r0, #0
		BEQ      |loc_0800FCFC|
		ADD r1, r4, #0
		ADD r0, sp, #0x6c
		BL       |loc_0800FE78|
		LDR r0, [r7]
		LDR r1, [sp, #0x74]
		CMP r0, r1
		BGE      |loc_0800FCFC|
		LDR r0, [sp, #0x6c]
		LDR r1, [r7, #8]
		CMP r0, r1
		BGE      |loc_0800FCFC|
		LDR r0, [r7, #4]
		LDR r1, [sp, #0x78]
		CMP r0, r1
		BGE      |loc_0800FCFC|
		LDR r0, [sp, #0x70]
		LDR r1, [r7, #0xc]
		CMP r0, r1
		BGE      |loc_0800FCFC|
		LDR r0, [r5, #0x1c]
		ADD r1, r4, #0
		LDRB r0, [r0]
		ADD r1, #0xff
		ADD r1, #0xb1
		CMP r0, #0
		BNE      |loc_0800FCF0|
		LDRB r1, [r1, #8]
		MOV r0, #1
		CMP r1, #0
		BNE      |loc_0800FC88|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf9fa
|unk_0800FCE0|
		DCD     0x080726AC
		DCD     0x08711274
		DCD     0x000003FF
		DCD     0x0877C678
|loc_0800FCF0|
		LDRB r1, [r1, #9]
		MOV r0, #1
		CMP r1, #0
		BNE      |loc_0800FC88|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf9fa
|loc_0800FCFC|
		ADD r2, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x10180
		B        |inc_0x0158_0x143f2| + 0xf9fa
