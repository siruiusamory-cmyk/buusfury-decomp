	CODE16
|loc_08010192|
		LDRB r3, [r4, #0x11]
		LDR r2, [r4, #0x50]
		LSL r3, r3, #4
		ADD r2, r2, r3
		LDRB r3, [r4, #0x10]
		LSL r3, r3, #2
		ADD r2, r2, r3
		LDR r2, [r2, #4]
		MOV r3, #0xe
		STR r2, [r4, #0x54]
		LDR r1, [r1]
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #0x18]
		ADD r0, r1, #0
		STR r0, [sp, #0x1c]
		STR r1, [sp, #0x14]
		LDR r1, [sp, #0x18]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0x91
		STR r1, [sp, #0x20]
		LDRB r2, [r0, #0xd]
		LSR r2, r2, #1
		ADD r1, r1, r2
		STR r1, [r4, #4]
		LDRSB r2, [r0, r3]
		LDR r1, [sp, #0x1c]
		MOV r3, #0xf
		ADD r1, r1, r2
		STR r1, [sp, #0x14]
		LDRSB r0, [r0, r3]
		LDR r1, [sp, #0x20]
		MOV r3, #4
		ADD r0, r1, r0
		STR r0, [sp, #0x18]
		LDR r1, [sp, #0x1c]
		LDR r0, [r4, #0x54]
		LDRSB r2, [r0, r3]
		MOV r3, #0x14
		ADD r1, r1, r2
		ADD r2, r4, #0
		ADD r2, #0xff
		ADD r2, #0x61
		MOV lr, r2
		LDRSH r2, [r2, r3]
		MOV ip, r1
		MOV r3, #5
		ADD ip, r2
		LDRSB r2, [r0, r3]
		LDR r1, [sp, #0x20]
		MOV r3, #0x16
		ADD r1, r1, r2
		MOV r2, lr
		LDRSH r2, [r2, r3]
		LDRB r3, [r0, #6]
		LDRB r0, [r0, #7]
		ADD r2, r1, r2
		MOV r1, ip
		ADD r3, ip
		MOV ip, r2
		ADD ip, r0
		LDR r0, [r7, #8]
		CMP r1, r0
		BGE      |loc_0801022E|
		LDR r0, [r7]
		CMP r0, r3
		BGE      |loc_0801022E|
		LDR r0, [r7, #0xc]
		CMP r2, r0
		BGE      |loc_0801022E|
		LDR r0, [r7, #4]
		CMP r0, ip
		BGE      |loc_0801022E|
		MOV r0, #1
		B        |loc_08010230|
|loc_0801022C|
		B        |loc_080102BA|
