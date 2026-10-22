	CODE16
|sub_08021F7E|
|unk_08021F7E|
		MOV r0, #0
		DCW     0xE7FC
|loc_08021F82|
|unk_08021F82|
		LSL r0, r1, #0x1e
		LSR r0, r0, #0x1e
		CMP r0, #1
		DCW     0xD1C8
		LSL r0, r1, #1
		LSL r2, r1, #0x1c
		LSR r3, r2, #0x1e
		LSR r0, r0, #0x1e
		CMP r0, r3
		DCW     0xD1C2
		LSL r0, r1, #8
		LSR r0, r0, #8
		MOV r2, #0
		CMP r0, #0
		BEQ      |loc_08021FAA|
|loc_08021FA0|
		LSL r7, r0, #0x1f
		BPL      |loc_08021FA6|
		ADD r2, #1
|loc_08021FA6|
		LSR r0, r0, #1
		BNE      |loc_08021FA0|
|loc_08021FAA|
		LSL r0, r1, #3
		LSR r0, r0, #0x1b
		CMP r2, r0
		DCW     0xD1B4
		LDRH r0, [r4, #0x10]
		CMP r3, r0
		BNE      |loc_08021FC0|
		LSL r0, r1, #8
		LSR r0, r0, #0x16
		STRH r0, [r4, #0xc]
		B        |loc_08021FD0|
|loc_08021FC0|
		ADD r0, #1
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1e
		CMP r0, r3
		DCW     0xD1A8
		LSL r0, r1, #0x12
		LSR r0, r0, #0x16
		STRH r0, [r4, #0xc]
|loc_08021FD0|
		LDRH r0, [r4, #0x10]
		ADD r0, #1
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1e
		STRH r0, [r4, #0x10]
		MOV r0, #1
		DCW     0xE7CE
