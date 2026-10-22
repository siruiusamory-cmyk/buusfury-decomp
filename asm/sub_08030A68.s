	CODE16
|sub_08030A68|
|unk_08030A68|
		LDR r1, [r0, #0x24]
		LDR r2, [r0, #0x28]
		ADD r1, r1, r2
		ADD r2, r0, #0
		ADD r2, #0x28
		SUB r3, r2, #4
		CMP r1, #0
		STR r1, [r0, #0x24]
		BGE      |loc_08030A86|
		NEG r1, r1
		STR r1, [r3]
		LDR r1, [r0, #0x28]
		NEG r1, r1
		STR r1, [r2]
		B        |loc_08030A9A|
|loc_08030A86|
		MOV r4, #0x55
		LSL r4, r4, #8
		CMP r1, r4
		BLE      |loc_08030A9A|
		LSL r4, r4, #1
		SUB r1, r4, r1
		STR r1, [r3]
		LDR r1, [r0, #0x28]
		NEG r1, r1
		STR r1, [r2]
|loc_08030A9A|
		LDR r1, [r0, #0x24]
		ASR r1, r1, #8
		STR r1, [r0, #0x1c]
		B        |loc_08030A64|
