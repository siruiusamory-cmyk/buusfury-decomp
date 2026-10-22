	CODE16
|sub_0803BA84|
|unk_0803BA84|
		LDR r0, [sp, #0x24]
		ADD r7, r4, #0
		ADD r7, #0xff
		ADD r7, #0xa5
		STR r0, [sp, #0x3c]
		LDR r0, [r7]
		STR r0, [sp, #0x40]
		LDR r0, [sp, #0x24]
		LDR r1, [r5]
		SUB r0, r0, r1
		STR r0, [sp, #0x20]
		BPL      |loc_0803BA9E|
		NEG r0, r0
|loc_0803BA9E|
		CMP r0, #0
		BLE      |sub_0803BABE|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x3c
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |sub_0803BABE|
		LDR r0, [sp, #0x3c]
		STR r0, [r5]
		LDR r0, [sp, #0x40]
		STR r0, [r6]
		B        |loc_0803BAEE|
