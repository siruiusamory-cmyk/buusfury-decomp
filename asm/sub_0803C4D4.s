	CODE16
|sub_0803C4D4|
|unk_0803C4D4|
; cited by 0x0803C470 (a pc-relative load targets 0x0803C4D8)
		MOV r0, #0
		POP {r4, pc}
	INCBIN  baserom.gba_0x3c4d8_0x3c4dc.extracted
		PUSH {r4, r5, r6, r7, lr}
		LDR r5, [r1, #4]
		MOV r1, #0x14
		ADD r4, r0, #0
		ADD r0, r5, #0
		SUB sp, #0x24
		BL       |Record_SelectIndexed|
		ADD r0, r5, #0
		BL       |sub_0800EE78|
		ADD r1, r5, #0
		ADD r0, sp, #0xc
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		LDR r0, [r4, #8]
		MOV r7, #0
		SUB r0, r0, r1
		LDR r1, [r4, #0xc]
		LDR r2, [sp, #0x20]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		STR r1, [sp, #8]
		ADD r1, r0, #0
		LDR r0, [sp, #8]
		LSL r2, r1, #1
		LSL r3, r0, #2
		ADD r0, r3, r0
		NEG r6, r0
		CMP r2, r6
		BGE      |loc_0803C53A|
		STR r7, [r4, #0x14]
		B        |inc_0x351c0_0x3d4d0| + 0x73a2
|loc_0803C53A|
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		CMP r1, r6
		BGE      |loc_0803C54A|
		MOV r0, #1
		STR r0, [r4, #0x14]
		B        |inc_0x351c0_0x3d4d0| + 0x73a2
|loc_0803C54A|
		CMP r2, r0
		BLE      |loc_0803C554|
		MOV r0, #4
		STR r0, [r4, #0x14]
		B        |inc_0x351c0_0x3d4d0| + 0x73a2
|loc_0803C554|
		CMP r1, r0
		BLE      |sub_0803C55E|
		MOV r0, #3
		STR r0, [r4, #0x14]
		B        |inc_0x351c0_0x3d4d0| + 0x73a2
