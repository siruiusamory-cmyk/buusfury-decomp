	CODE16
|sub_08015E16|
|unk_08015E16|
; cited by 0x08015BC0 (a pc-relative load targets 0x08015E80)
		STR r7, [r1, #0x10]
		STR r7, [r1, #8]
		LDR r1, [r0, #0x20]
		STR r7, [r1, #0x10]
		STR r7, [r1, #8]
		LDR r1, [r0, #0x2c]
		LDR r2, [r0, #0x24]
		SUB r1, r1, r2
		LDR r2, [r0, #0x34]
		SUB r1, #0x28
		STR r2, [r0, #0x38]
		LDR r7, [r0, #0x4c]
|loc_08015E2E|
		LDR r2, [r0, #0x38]
		ADD r5, r6, #0
		CMP r7, r2
		BLE      |loc_08015E4E|
		LSL r3, r2, #1
		ADD r3, r3, r2
		LSL r3, r3, #2
		ADD r3, r3, r4
		LDR r3, [r3, #0xc]
		ADD r6, r3, r6
		ADD r6, #0xa
		CMP r6, r1
		BGT      |loc_08015E4E|
		ADD r2, #1
		STR r2, [r0, #0x38]
		B        |loc_08015E2E|
|loc_08015E4E|
		ADD r1, r0, #0
		ADD r1, #0x24
		ADD r2, r1, #0
		LDR r3, [r0, #0x24]
		LDR r4, [r0, #0x2c]
		ADD r2, #8
		LDR r1, [r0, #0x28]
		LDR r2, [r2, #4]
		ADD r3, r3, r4
		ADD r1, r1, r2
		STR r1, [sp, #4]
		ASR r1, r1, #1
		ASR r2, r3, #1
		STR r1, [sp, #4]
		STR r1, [sp, #0xc]
		STR r3, [sp]
		STR r2, [sp]
		ADD r1, r2, #0
		STR r2, [sp, #8]
		LSR r2, r5, #0x1f
		ADD r2, r2, r5
		ASR r2, r2, #1
		SUB r1, r1, r2
		STR r1, [r0, #0x48]
		B        |inc_0x153f2_0x1a3f2| + 0xa1e
	INCBIN  baserom.gba_0x15e80_0x15e94.extracted
