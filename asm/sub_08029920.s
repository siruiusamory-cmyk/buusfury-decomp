	CODE16
|sub_08029920|
|unk_08029920|
		LDR r1, [r0]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r4, r0, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BGT      |loc_0802993C|
		MOV r0, #1
		DCW     0xE7EF
|loc_0802993C|
		LDR r0, [pc, #0x30]
		LDR r0, [r0, #4]
		LSL r0, r0, #0x1a
		BNE      |loc_0802995A|
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		STR r5, [sp, #0x10]
		LDR r2, [r4]
		ADD r0, r4, #0
		LDR r3, [r2, #0x5c]
		MOV r1, sp
		ADD r2, r3, r2
		BL       |loc_08046AA4|
|loc_0802995A|
		MOV r0, #0
		DCW     0xE7DE
	INCBIN  baserom.gba_0x2995e_0x29962.extracted
