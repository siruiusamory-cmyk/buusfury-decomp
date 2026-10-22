	CODE16
|loc_0803B91E|
		SUB r6, #1
		CMP r6, #0
		BLE      |loc_0803B926|
		B        |inc_0x351c0_0x3d4d0| + 0x6608
|loc_0803B926|
		LDR r1, [sp, #0x54]
		MOV r0, #1
		STR r1, [r7, #0xc]
		LDR r1, [sp, #0x58]
		STR r0, [r7, #0x14]
		STR r1, [r7, #0x10]
		B        |inc_0x351c0_0x3d4d0| + 0x6660
