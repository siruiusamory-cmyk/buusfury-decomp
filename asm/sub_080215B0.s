	CODE16
|sub_080215B0|
|unk_080215B0|
		LDR r7, [pc, #0x174]
		LDRB r5, [r7]
		LDRB r0, [r7, #1]
		MUL r5, r0
		LDR r0, [pc, #0x170]
		ADD r1, r5, #0
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		SUB r0, r7, #6
		LDR r0, [r0]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_080215E0|
		ADD r1, r5, #0
		SUB r0, r7, #6
		LDR r0, [r0]
		BL       |sub_08011732|
		ADD r1, r5, #0
		SUB r0, r7, #6
		LDR r0, [r0]
		BL       |loc_0801124C|
|loc_080215E0|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x148]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [pc, #0x13c]
		MOV r2, #0x3a
		SUB r1, #2
		STR r1, [r4, #0x28]
		STRB r2, [r4, #8]
		LDRB r2, [r7]
		LDRB r3, [r7, #1]
		LSL r0, r0, #5
		LDR r1, [r1, #8]
		MUL r2, r3
		LDR r3, [pc, #0x134]
		ADD r0, r0, r3
		BL       |Thunk_VramCopy|
		LDR r0, [pc, #0x130]
		STR r0, [r4]
		LDR r0, [pc, #0x130]
		LDMIA r6!, {r1, r2}
		STR r0, [r4]
		STR r1, [r4, #0x2c]
		STR r2, [r4, #0x30]
		MOV r0, #0
		STR r0, [r4, #0x34]
		LDR r0, [sp, #0x10]
		MOV r1, #0x46
		STR r0, [r4, #0x44]
		MOV r0, #2
		STR r0, [r4, #0x38]
		LDR r0, [sp, #0xc]
		SUB r6, #8
		CMP r0, #2
		STR r0, [r4, #0x40]
		BLT      |loc_0802162E|
		MOV r1, #0x64
|loc_0802162E|
		STR r1, [r4, #0x3c]
		ADD r0, r4, #0
		ADD r4, #0x48
		LDMIA r6!, {r1, r2}
		STMIA r4!, {r1, r2}
		DCW     0xE7B8
		PUSH {r4, r5}
		LDR r2, [r0, #0x44]
		LDR r1, [r0, #0x34]
		LDR r3, [r0, #0x3c]
		LDR r4, [r0, #0x40]
		SUB sp, #8
		CMP r2, #0
		BEQ      |loc_080216D4|
		CMP r4, #0
		BEQ      |loc_08021668|
		CMP r4, #1
		BEQ      |loc_08021682|
		CMP r4, #2
		BEQ      |loc_0802169C|
		CMP r4, #3
		BNE      |loc_080216C0|
		LDRH r2, [r2, #2]
		LSL r5, r2, #0x1b
		LSR r5, r5, #0x1f
		BEQ      |loc_080216B6|
		ADD r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_08021668|
		LDRH r2, [r2, #2]
		LSL r5, r2, #0x18
		LSR r5, r5, #0x1f
		BEQ      |loc_08021676|
		ADD r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_08021676|
		LSL r2, r2, #0x19
		LSR r2, r2, #0x1f
		BEQ      |loc_080216C0|
		SUB r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_08021682|
		LDRH r2, [r2, #2]
		LSL r5, r2, #0x19
		LSR r5, r5, #0x1f
		BEQ      |loc_08021690|
		ADD r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_08021690|
		LSL r2, r2, #0x18
		LSR r2, r2, #0x1f
		BEQ      |loc_080216C0|
		SUB r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_0802169C|
		LDRH r2, [r2, #2]
		LSL r5, r2, #0x1a
		LSR r5, r5, #0x1f
		BEQ      |loc_080216AA|
		ADD r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_080216AA|
		LSL r2, r2, #0x1b
		LSR r2, r2, #0x1f
		BEQ      |loc_080216C0|
		SUB r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_080216B6|
		LSL r2, r2, #0x1a
		LSR r2, r2, #0x1f
		BEQ      |loc_080216C0|
		SUB r1, #2
		STR r1, [r0, #0x34]
|loc_080216C0|
		LDR r1, [r0, #0x34]
		CMP r1, #0x10
		BGE      |loc_080216CA|
		MOV r1, #0x10
		STR r1, [r0, #0x34]
|loc_080216CA|
		LDR r1, [r0, #0x34]
		CMP r1, r3
		BLE      |loc_080216F2|
		STR r3, [r0, #0x34]
		B        |loc_080216F2|
|loc_080216D4|
		LDR r2, [r0, #0x38]
		ADD r1, r1, r2
		STR r1, [r0, #0x34]
		CMP r1, r3
		BLT      |Object_ClearFields3|
		MOV r1, #1
		MVN r1, r1
		STR r1, [r0, #0x38]
		B        |loc_080216F2|
