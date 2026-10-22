	CODE16
|loc_080340A8|
|unk_080340A8|
		LDR r2, [r5]
		ASR r1, r1, #8
		ASR r2, r2, #8
		STR r2, [sp, #0x40]
		STR r2, [sp, #0x38]
		MOV r2, #0x38
		STR r1, [sp, #0x34]
		STR r1, [sp, #0x3c]
		MOV r1, #1
		LSL r1, r1, #0xa
		STR r1, [sp, #4]
		STR r2, [sp, #8]
		STR r0, [sp]
		ADD r5, sp, #0x3c
		B        |sub_080340C8|
|loc_080340C6|
		B        |inc_0x331c0_0x341c0| + 0xf24
