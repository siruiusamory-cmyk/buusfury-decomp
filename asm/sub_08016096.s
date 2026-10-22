	CODE16
|sub_08016096|
|unk_08016096|
		LDR r2, [r0, #0x48]
		STR r2, [r1]
		LDR r2, [r0, #0x30]
		SUB r2, #8
		STR r2, [r1, #4]
		LDR r2, [r0, #0x34]
		LDR r3, [r0, #0x3c]
		CMP r3, r2
		BLE      |loc_080160C6|
		ADD r4, r0, #0
		ADD r4, #0x4c
|loc_080160AC|
		LSL r3, r2, #1
		ADD r3, r3, r2
		LSL r3, r3, #2
		ADD r3, r3, r4
		LDR r3, [r3, #0xc]
		LDR r5, [r1]
		ADD r2, #1
		ADD r3, r3, r5
		ADD r3, #0xa
		STR r3, [r1]
		LDR r3, [r0, #0x3c]
		CMP r3, r2
		BGT      |loc_080160AC|
|loc_080160C6|
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0xca0
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		ADD r0, #0xff
		ADD r0, #1
		LDR r0, [r0, #0x10]
		ADD r7, r1, #0
		CMP r0, #0
		SUB sp, #0x1c
		BNE      |loc_080160E2|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x9cc
|loc_080160E2|
		LDR r2, [r4, #0x1c]
		MOV r0, #1
		LDR r1, [r2, #0x10]
		CMP r1, #0
		BEQ      |inc_0x153f2_0x1a3f2| + 0xd32
		LDR r1, [r4, #4]
		ADD r1, #0xff
		ADD r1, #1
		LDR r1, [r1, #0xc]
		LDR r3, [r4, #8]
		CMP r1, r3
		BNE      |sub_0801611C|
		LDR r3, [r4, #0x3c]
		ADD r1, r0, #0
		CMP r3, #0
		BNE      |loc_08016104|
		MOV r1, #0
|loc_08016104|
		STR r1, [r2, #8]
		LDR r1, [r4, #0x20]
		LDR r2, [r4, #0x4c]
		LDR r3, [r4, #0x3c]
		SUB r2, #1
		CMP r2, r3
		BEQ      |loc_08016116|
		MOV r2, #1
		B        |loc_08016118|
|loc_08016116|
		MOV r2, #0
|loc_08016118|
		STR r2, [r1, #8]
		B        |inc_0x153f2_0x1a3f2| + 0xd32
