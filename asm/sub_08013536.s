	CODE16
|sub_08013536|
|unk_08013536|
		LDRH r1, [r0, #0x20]
		SUB r1, r1, r3
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
|loc_0801353E|
		STRH r1, [r0, #0x20]
		LDRH r2, [r0, #0x20]
		CMP r2, r1
		BNE      |loc_0801353E|
		B        |inc_0x0158_0x143f2| + 0x133da
|loc_08013548|
|unk_08013548|
		LSL r4, r4, #0x1f
		BEQ      |loc_08013570|
		LDRH r4, [r0, #0x1e]
		CMP r4, r1
		BGE      |loc_0801355E|
		ADD r1, r2, #0
|loc_08013554|
		STRH r1, [r0, #0x1e]
		LDRH r2, [r0, #0x1e]
		CMP r2, r1
		BNE      |loc_08013554|
		B        |inc_0x0158_0x143f2| + 0x133da
|loc_0801355E|
		LDRH r1, [r0, #0x1e]
		SUB r1, r1, r3
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
|loc_08013566|
		STRH r1, [r0, #0x1e]
		LDRH r2, [r0, #0x1e]
		CMP r2, r1
		BNE      |loc_08013566|
		B        |inc_0x0158_0x143f2| + 0x133da
|loc_08013570|
		MOV r3, #0x1a
		LDRSH r4, [r0, r3]
		CMP r4, r1
		BGE      |loc_08013584|
|loc_08013578|
		STRH r2, [r0, #0x1a]
		MOV r3, #0x1a
		LDRSH r1, [r0, r3]
		CMP r1, r2
		BNE      |loc_08013578|
		B        |inc_0x0158_0x143f2| + 0x133da
|loc_08013584|
		LDRH r2, [r0, #0x1a]
		SUB r1, r2, r1
		LSL r1, r1, #0x10
		ASR r1, r1, #0x10
|loc_0801358C|
		STRH r1, [r0, #0x1a]
		MOV r3, #0x1a
		LDRSH r2, [r0, r3]
		CMP r2, r1
		BNE      |loc_0801358C|
		B        |inc_0x0158_0x143f2| + 0x133da
