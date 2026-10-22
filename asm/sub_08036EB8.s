	CODE16
|sub_08036EB8|
|unk_08036EB8|
		ADD r0, r2, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r3}
		LDR r0, [r0]
		ASR r3, r3, #8
		ASR r0, r0, #8
		STR r0, [sp, #4]
		ADD r0, r3, #0
		STR r0, [sp, #8]
		STR r3, [sp]
		LDR r3, [sp, #4]
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		STR r3, [sp, #0xc]
		LDMIA r0!, {r3}
		LDR r0, [r0]
		ASR r3, r3, #8
		ASR r0, r0, #8
		STR r0, [sp, #4]
		ADD r0, r3, #0
		STR r3, [sp]
		LDR r3, [sp, #4]
		STR r0, [sp, #0x10]
		STR r3, [sp, #0x14]
		LDR r3, [sp, #0x10]
		LDR r0, [sp, #8]
		LDR r4, [sp, #0x14]
		SUB r0, r0, r3
		LDR r3, [sp, #0xc]
		STR r0, [sp]
		SUB r3, r3, r4
		ADD r4, r0, #0
		CMP r0, #0
		STR r3, [sp, #4]
		STR r3, [sp, #0x1c]
		STR r0, [sp, #0x18]
		BGE      |loc_08036F08|
		NEG r0, r4
|loc_08036F08|
		ADD r3, r0, #0
		LDR r0, [sp, #0x1c]
		CMP r0, #0
		BGE      |loc_08036F12|
		NEG r0, r0
|loc_08036F12|
		STR r0, [sp, #4]
		ADD r0, r3, #0
		STR r3, [sp]
		LDR r3, [sp, #4]
		CMP r0, #0x10
		BGT      |loc_08036F22|
		CMP r3, #0x10
		BLE      |loc_08036F26|
|loc_08036F22|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1cf2
|loc_08036F26|
		MOV r0, #0xff
		ADD r0, #0xa9
		ADD r1, r1, r0
		LDR r0, [r0, r2]
		LDR r1, [r1]
		SUB r0, r0, r1
		ASR r0, r0, #0xa
		BPL      |loc_08036F38|
		NEG r0, r0
|loc_08036F38|
		ADD r1, r0, #0
		MOV r0, #1
		CMP r1, #0x10
		BLT      |inc_0x351c0_0x3d4d0| + 0x1cf2
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1cf2
