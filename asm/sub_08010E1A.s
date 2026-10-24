	CODE16
|sub_08010E1A|
|unk_08010E1A|
		CMP r7, #0xb
		BEQ      |inc_0x0158_0x143f2| + 0x10d9c
		CMP r7, #0x1a
		BEQ      |inc_0x0158_0x143f2| + 0x10d9e
		CMP r7, #0x28
		BNE      |loc_08010EF2|
		ADD r1, r4, #0
		LDMIA r5!, {r6, r7}
		SUB r5, #8
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r0, [sp]
		CMP r0, r6
		BLE      |loc_08010E42|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r6, [sp]
|loc_08010E42|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r0, [sp, #8]
		CMP r0, r6
		BGE      |loc_08010E5A|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r6, [sp, #8]
|loc_08010E5A|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r0, [sp, #4]
		CMP r0, r7
		BLE      |loc_08010E72|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r7, [sp, #4]
|loc_08010E72|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r0, [sp, #0xc]
		CMP r0, r7
		BGE      |loc_08010E8A|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r7, [sp, #0xc]
|loc_08010E8A|
		LDR r0, [r5]
		SUB r0, r0, r6
		ADD r1, r0, #0
		MUL r0, r1
		LDR r1, [r5, #4]
		SUB r1, r1, r7
		ADD r2, r1, #0
		MUL r1, r2
		ADD r1, r0, r1
		LDR r0, [r5, #8]
		ADD r2, r0, #0
		MUL r0, r2
		CMP r0, r1
		BLE      |inc_0x0158_0x143f2| + 0x10e34
		LDR r0, [sp, #0x10]
		LDR r0, [r0, #0xc]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0x10e34
		ADD r5, #0xc
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |Battle_ComputeDamage|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x58]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x10cbe
|loc_08010ECA|
|unk_08010ECA|
		B        |loc_08010ECC|
|loc_08010ECC|
		LDR r2, [r2, #8]
		MOV r3, #0x68
		LDRB r6, [r2]
		MUL r3, r6
		ADD r2, r3, r2
		ADD r1, r2, r1
		LDRB r1, [r1, #0x14]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #3
		ADD r0, r1, r0
		BL       |inc_0x153f2_0x1a3f2| + 0x1d3a
		MOV r0, #0
		LDR r1, [pc, #0x40]
		B        |inc_0x0158_0x143f2| + 0x10da0
|loc_08010EEC|
|unk_08010EEC|
		B        |inc_0x0158_0x143f2| + 0x10de8
|loc_08010EEE|
|unk_08010EEE|
		B        |inc_0x0158_0x143f2| + 0x10e46
|loc_08010EF0|
|unk_08010EF0|
		B        |inc_0x0158_0x143f2| + 0x10ebc
|loc_08010EF2|
|unk_08010EF2|
; cited by 0x08010B84 (a pc-relative load targets 0x08010F28)
		B        |loc_08010F1A|
		B        |loc_08010EFC|
		B        |inc_0x0158_0x143f2| + 0x10ea4
		STR r0, [r1]
		B        |loc_08010F1A|
|loc_08010EFC|
		LDR r2, [r2, #8]
		MOV r3, #0x68
		LDRB r6, [r2]
		MUL r3, r6
		ADD r2, r3, r2
		ADD r1, r2, r1
		LDRB r1, [r1, #0x14]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #3
		ADD r0, r1, r0
		BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
		LDR r1, [pc, #0x14]
		STR r4, [r1]
