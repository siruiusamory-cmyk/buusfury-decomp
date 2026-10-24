	CODE16
|sub_0803CA10|
	ADD      r2, r1, #0
	SUB      r2, #0x10
	ASR      r2, r2, #3
	ADD      r2, #1
	STRB     r2, [r4, #0x11]
	CMP      r1, #0x10
	BNE      |loc_0803CA24|
	ADD      r1, r4, #0
	BL       |loc_0803C8FC|
|loc_0803CA24|
	LDRB     r0, [r4, #0x11]
	CMP      r0, #4
	BCC      |loc_0803CA38|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803CA38|
	POP      {r4, pc}
|sub_0803CA3A|
|unk_0803CA3A|
		PUSH {r4, r5, r6, lr}
		LDR r0, [pc, #0xe8]
		ADD r4, r1, #0
		LDR r1, [r0]
		MOV r5, #0
		CMP r1, #0
		SUB sp, #0x38
		BEQ      |inc_0x351c0_0x3d4d0| + 0x793a
		MOV r0, #0xff
		ADD r0, #0xcd
		LDR r0, [r0, r1]
		CMP r0, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x793a
		ADD r0, sp, #0x28
		BL       |Object_GetPoints|
		ADD r1, r4, #0
		ADD r0, sp, #0x18
		BL       |Object_GetPoints|
		LDR r0, [sp, #0x18]
		LDR r1, [sp, #0x20]
		LDR r2, [sp, #0x24]
		ADD r1, r0, r1
		LDR r0, [sp, #0x1c]
		STR r1, [sp, #8]
		ADD r0, r0, r2
		STR r0, [sp, #0xc]
		ASR r1, r1, #1
		ASR r0, r0, #1
		STR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x10]
		LDR r1, [sp, #0x30]
		LDR r0, [sp, #0x28]
		LDR r2, [sp, #0x34]
		ADD r1, r0, r1
		LDR r0, [sp, #0x2c]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0xc]
		ADD r0, r1, #0
		STR r1, [sp]
		STR r1, [sp, #8]
		LDR r1, [sp, #0x10]
		LDR r2, [sp, #0x14]
		SUB r0, r0, r1
		LDR r1, [sp, #0xc]
		MOV r6, #1
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #4]
		STR r0, [sp]
		BGE      |loc_0803CAB4|
		NEG r2, r0
|loc_0803CAB4|
		ADD r3, r1, #0
		CMP r1, #0
		BGE      |loc_0803CABC|
		NEG r3, r1
|loc_0803CABC|
		CMP r2, r3
		BLE      |loc_0803CAD0|
		CMP r0, #0
		BLE      |loc_0803CACA|
		MOV r0, #3
		STRB r0, [r4, #0x10]
		B        |inc_0x351c0_0x3d4d0| + 0x791a
|loc_0803CACA|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		B        |inc_0x351c0_0x3d4d0| + 0x791a
|loc_0803CAD0|
		CMP r1, #0
		BLE      |sub_0803CAD8|
		STRB r5, [r4, #0x10]
		B        |inc_0x351c0_0x3d4d0| + 0x791a
