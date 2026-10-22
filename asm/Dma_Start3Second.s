|Dma_Start3Second|
	CODE16
|unk_08008306|
		B        |loc_08008364|
|loc_08008308|
|unk_08008308|
		MOV r6, #1
		EOR r6, r4
		LDR r2, [sp, #0x48]
		LSL r6, r6, #5
		ADD r2, r2, r6
		LDR r6, [pc, #0x194]
		ADD r7, r2, r6
		LDR r2, [sp, #0x20]
		LSL r6, r2, #1
		LDR r2, [sp, #0x1c]
		SUB r6, #0x20
		LSL r2, r2, #0x1b
		LSR r2, r2, #0x1b
		STR r6, [sp, #0xc]
		LSL r6, r2, #6
		MOV ip, r6
		ADD ip, r7
		LDR r6, [r0, #0x10]
		LSL r7, r2, #5
		MOV lr, r6
		ADD lr, r7
		CMP r2, #0x20
		BGE      |loc_08008364|
		LDR r6, [sp, #0xc]
		LDR r7, [pc, #0x170]
		LSL r6, r6, #0xf
		LSR r6, r6, #0x10
		STR r6, [sp, #0x40]
|loc_08008340|
		MOV r6, lr
		STR r6, [r7]
		MOV r6, ip
		STR r6, [r7, #4]
		LDR r6, [sp, #0x40]
		STRH r6, [r7, #8]
		MOV r6, #1
		LSL r6, r6, #0xf
		STRH r6, [r7, #0xa]
		MOV r6, lr
		ADD r6, #0x20
		MOV lr, r6
		MOV r6, ip
		ADD r6, #0x40
		ADD r2, #1
		CMP r2, #0x20
		MOV ip, r6
		BLT      |loc_08008340|
|loc_08008364|
		LDR r2, [sp, #0x18]
		CMP r2, #0
		BGE      |loc_080083CA|
		MOV r6, #1
		EOR r6, r4
		LSL r6, r6, #5
		LSL r2, r5, #0xb
		ADD r2, r2, r6
		LDR r6, [pc, #0x130]
		ADD r7, r2, r6
		LDR r2, [sp, #0x18]
		MOV r6, #0x20
		LSL r2, r2, #0x1c
		LSR r2, r2, #0x1b
		SUB r6, r6, r2
		STR r6, [sp, #0xc]
		LSL r6, r1, #6
		ADD r6, r6, r7
		MOV ip, r6
		LDR r6, [r0, #0x14]
		LSL r7, r1, #5
		ADD r6, r6, r7
		MOV lr, r6
		ADD lr, r2
		ADD ip, r2
		ADD r2, r1, #0
		CMP r1, r3
		BGE      |loc_080083CA|
		LDR r6, [sp, #0xc]
		LDR r7, [pc, #0x10c]
		LSL r6, r6, #0xf
		LSR r6, r6, #0x10
		STR r6, [sp, #0x3c]
|loc_080083A6|
		MOV r6, lr
		STR r6, [r7]
		MOV r6, ip
		STR r6, [r7, #4]
		LDR r6, [sp, #0x3c]
		STRH r6, [r7, #8]
		MOV r6, #1
		LSL r6, r6, #0xf
		STRH r6, [r7, #0xa]
		MOV r6, lr
		ADD r6, #0x20
		MOV lr, r6
		MOV r6, ip
		ADD r6, #0x40
		ADD r2, #1
		CMP r2, r3
		MOV ip, r6
		BLT      |loc_080083A6|
|loc_080083CA|
		LSL r2, r5, #0xb
		LSL r6, r4, #5
		MOV ip, r2
		ADD r2, r2, r6
		MOV lr, r6
		LDR r6, [pc, #0xd0]
		ADD r7, r2, r6
		LDR r6, [sp, #0x14]
		STR r7, [sp, #0xc]
		LSL r7, r6, #1
		LDR r2, [sp, #0x10]
		STR r7, [sp, #0x38]
		SUB r2, r2, r6
		LSL r6, r2, #1
		STR r6, [sp, #0x34]
		STR r7, [sp, #8]
		BEQ      |loc_08008436|
		LDR r7, [sp, #0xc]
		LSL r2, r1, #6
		ADD r2, r2, r7
		LDR r7, [sp, #8]
		ADD r2, r2, r7
		STR r2, [sp, #4]
		LDR r2, [r0, #0x18]
		LSL r7, r1, #5
		ADD r2, r2, r7
		LDR r7, [sp, #8]
		ADD r2, r2, r7
		STR r2, [sp]
		ADD r2, r1, #0
		CMP r1, r3
		BGE      |loc_08008436|
		LSL r6, r6, #0xf
		LSR r6, r6, #0x10
		LDR r7, [pc, #0x9c]
		STR r6, [sp, #0x30]
|loc_08008412|
		LDR r6, [sp]
		STR r6, [r7]
		LDR r6, [sp, #4]
		STR r6, [r7, #4]
		LDR r6, [sp, #0x30]
		STRH r6, [r7, #8]
		MOV r6, #1
		LSL r6, r6, #0xf
		STRH r6, [r7, #0xa]
		LDR r6, [sp]
		ADD r2, #1
		ADD r6, #0x20
		STR r6, [sp]
		LDR r6, [sp, #4]
		ADD r6, #0x40
		STR r6, [sp, #4]
		CMP r2, r3
		BLT      |loc_08008412|
|loc_08008436|
		LDR r2, [sp, #0x20]
		CMP r2, #0x10
		BLE      |inc_0x0158_0x143f2| + 0x835a
		MOV r6, #1
		EOR r6, r4
		MOV r2, ip
		LSL r6, r6, #5
		ADD r2, r2, r6
		LDR r6, [pc, #0x60]
		LSL r7, r1, #6
		ADD r2, r2, r6
		LDR r6, [sp, #0x20]
		MOV ip, r7
		ADD ip, r2
		LDR r2, [r0, #0x1c]
		LSL r7, r1, #5
		LSL r6, r6, #1
		SUB r6, #0x20
		ADD r2, r2, r7
		CMP r1, r3
		BGE      |inc_0x0158_0x143f2| + 0x835a
		LSL r6, r6, #0xf
		LSR r6, r6, #0x10
		LDR r7, [pc, #0x44]
		STR r6, [sp, #0x2c]
|loc_08008468|
|unk_08008468|
; cited by 0x080080A8 (a pc-relative load targets 0x08008488)
		STR r2, [r7]
		MOV r6, ip
		STR r6, [r7, #4]
		LDR r6, [sp, #0x2c]
		STRH r6, [r7, #8]
		MOV r6, #1
		LSL r6, r6, #0xf
		STRH r6, [r7, #0xa]
		MOV r6, ip
		ADD r6, #0x40
		ADD r2, #0x20
		ADD r1, #1
		CMP r1, r3
		MOV ip, r6
		B        |inc_0x0158_0x143f2| + 0x8358
	INCBIN  baserom.gba_0x8486_0x84a6.extracted
