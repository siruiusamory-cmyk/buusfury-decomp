	CODE16
|sub_0801299E|
|unk_0801299E|
		LDR r0, [sp, #0xc]
		LDR r1, [r4]
		LSL r0, r0, #0x1d
		STR r1, [sp, #8]
		LDR r1, [sp, #0x20]
		LSR r0, r0, #0x1d
		LSL r1, r1, #0x1f
		BPL      |loc_080129E6|
		CMP r0, #2
		BLT      |loc_080129B6|
		CMP r0, #5
		BLE      |loc_080129E6|
|loc_080129B6|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x10]
		ADD r0, #4
		LSR r0, r0, #3
		LSL r0, r0, #3
		STR r0, [sp]
		LDR r0, [pc, #0x34c]
		STR r1, [sp, #4]
		LDR r0, [r0, #8]
		MOV r1, sp
		ADD r2, r7, #0
		BL       |loc_080097C2|
		CMP r0, #0
		BEQ      |loc_080129E6|
		LDR r0, [sp]
		LDR r1, [r4, #4]
		LSL r0, r0, #8
		STR r0, [r6]
		STR r1, [r5]
		LDR r0, [sp]
		LSL r1, r0, #8
		STR r1, [sp, #8]
		STR r0, [sp, #0xc]
|loc_080129E6|
		LDR r0, [sp, #0x10]
		LDR r1, [sp, #0x20]
		LSL r0, r0, #0x1d
		LSR r0, r0, #0x1d
		LSL r1, r1, #0x1e
		BPL      |inc_0x0158_0x143f2| + 0x12842
		CMP r0, #2
		BLT      |loc_080129FA|
		CMP r0, #5
		BLE      |inc_0x0158_0x143f2| + 0x12842
|loc_080129FA|
		ADD r1, sp, #0xc
		LDMIA r1!, {r0, r1}
		STR r0, [sp]
		ADD r1, #4
		LSR r1, r1, #3
		LSL r1, r1, #3
		STR r1, [sp, #4]
		LDR r0, [pc, #0x304]
		MOV r1, sp
		ADD r2, r7, #0
		LDR r0, [r0, #8]
		BL       |loc_080097C2|
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0x12842
		ADD r1, sp, #4
		LDMIA r1!, {r0, r1}
		LSL r0, r0, #8
		STR r1, [r6]
		STR r0, [r5]
		B        |inc_0x0158_0x143f2| + 0x12842
