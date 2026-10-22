	CODE16
|sub_0801D95A|
	LSR      r1, r6, #1
	LSR      r4, r4, #4
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r0, sp, #0x3d0
	LSR      r4, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	ADD      r0, #0xff
	ADD      r0, #1
	ADD      r0, #0x38
	LDMIA    r0!, {r0, r2}
	SUB      r0, r2, r0
	LSL      r0, r0, #4
	ADD      r0, #0x24
	STR      r0, [r1, #4]
	MOV      r2, #0x12
	STR      r2, [r1]
	MOV      r0, #1
	BX       lr
|sub_0801D988|
|unk_0801D988|
		PUSH {r0, r4, r5, r6, r7, lr}
		SUB sp, #0x158
		MOV r2, #0xa0
		MOV r1, #0xf0
		ADD r0, sp, #0x11c
		BL       |loc_0803F540|
		MOV r3, #0
		MOV r2, #0x24
		ADD r1, sp, #0x11c
		LDR r0, [sp, #0x158]
		BL       |loc_08006718|
		LDR r2, [sp, #0x158]
		MOV r5, #1
		ADD r2, #0xff
		ADD r2, #0x51
		STR r2, [sp, #0x154]
		LDR r0, [r2]
		LDR r7, [pc, #0x2b8]
		CMP r0, #0
		BEQ      |loc_0801DA8A|
		LDR r2, [sp, #0x158]
		ADD r0, r5, #0
		ADD r2, #0xff
		ADD r2, #0x41
		LDR r1, [r2, #4]
		LDR r4, [sp, #0x158]
		ADD r4, #0xff
		ADD r4, #1
		LDR r3, [r4, #0x3c]
		CMP r3, #0
		BGT      |loc_0801D9CC|
		MOV r0, #0
|loc_0801D9CC|
		STR r0, [r1, #8]
		LDR r0, [r2, #8]
		LDR r2, [sp, #0x154]
		LDR r1, [r2]
		LDR r2, [r4, #0x3c]
		SUB r1, #1
		CMP r1, r2
		BLE      |loc_0801D9E0|
		MOV r1, #1
		B        |loc_0801D9E2|
|loc_0801D9E0|
		MOV r1, #0
|loc_0801D9E2|
		STR r1, [r0, #8]
		MOV r1, #0xa5
		MOV r3, #0x4b
		MOV r2, #0x2d
		ADD r6, sp, #0x11c
		ADD r0, r6, #0
		BL       |loc_080051B0|
		MOV r3, #0xe0
		MOV r2, #0x5e
		MOV r1, #0x10
		ADD r0, r6, #0
		BL       |loc_08005154|
		LDR r6, [pc, #0x26c]
		MOV r3, #0x68
		LDR r0, [r6, #0xc]
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		STR r0, [sp, #0x118]
		BL       |loc_08013C66|
		LDR r0, [r6, #8]
		ADD r3, sp, #0x100
		STR r0, [sp, #0x128]
		MOV r0, #0
		STRB r0, [r3, #0x1c]
		STRB r5, [r3, #0x1e]
		LDR r0, [pc, #0x24c]
		MOV r6, #0xaf
		STR r0, [sp, #0x13c]
		MOV r0, #0x28
		STR r0, [sp, #0x124]
		STR r6, [sp, #0x120]
		LDR r0, [r4, #0x18]
		LDR r2, [r4, #0x28]
		CMP r2, r0
		BNE      |loc_0801DA3A|
		MOV r0, #0x37
		B        |loc_0801DA44|
|loc_0801DA3A|
		CMP r2, r0
		BLE      |loc_0801DA42|
		MOV r0, #0x38
		B        |loc_0801DA44|
|loc_0801DA42|
		MOV r0, #0x39
|loc_0801DA44|
		LSL r0, r0, #2
		LDR r1, [r7, r0]
		ADD r5, r7, #0
		ADD r7, sp, #0x11c
		ADD r0, r7, #0
		BL       |sub_0803DC96|
		MOV r0, #0x34
		STR r0, [sp, #0x124]
		STR r6, [sp, #0x120]
		LDR r0, [r4, #0x1c]
		LDR r2, [r4, #0x2c]
		CMP r2, r0
		BNE      |loc_0801DA64|
		MOV r0, #0x3a
		B        |loc_0801DA6E|
|loc_0801DA64|
		CMP r2, r0
		BLE      |loc_0801DA6C|
		MOV r0, #0x3b
		B        |loc_0801DA6E|
|loc_0801DA6C|
		MOV r0, #0x3c
|loc_0801DA6E|
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r7, #0
		BL       |sub_0803DC96|
		MOV r0, #0x40
		STR r0, [sp, #0x124]
		STR r6, [sp, #0x120]
		LDR r0, [r4, #0x20]
		LDR r2, [r4, #0x30]
		CMP r2, r0
		BNE      |loc_0801DA8C|
		MOV r0, #0x3d
		B        |loc_0801DA96|
|loc_0801DA8A|
		B        |sub_0801DC20|
|loc_0801DA8C|
		CMP r2, r0
		BLE      |loc_0801DA94|
		MOV r0, #0x3e
		B        |loc_0801DA96|
|loc_0801DA94|
		MOV r0, #0x3f
|loc_0801DA96|
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r7, #0
		BL       |sub_0803DC96|
		MOV r0, #0xaf
		STR r0, [sp, #0x120]
		MOV r0, #0x4c
		STR r0, [sp, #0x124]
		LDR r0, [r4, #0x24]
		LDR r2, [r4, #0x34]
		CMP r2, r0
		BNE      |loc_0801DAB4|
		MOV r0, #0x40
		B        |loc_0801DABE|
|loc_0801DAB4|
		CMP r2, r0
		BLE      |loc_0801DABC|
		MOV r0, #0x41
		B        |loc_0801DABE|
|loc_0801DABC|
		MOV r0, #0x42
|loc_0801DABE|
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r7, #0
		BL       |sub_0803DC96|
		LDR r2, [sp, #0x154]
		LDR r0, [r4, #0x3c]
		MOV r3, #0x2c
		LSL r0, r0, #3
		ADD r0, r0, r2
		LDR r0, [r0, #4]
		LDR r2, [pc, #0x19c]
		LSL r0, r0, #4
		LSR r0, r0, #4
		MUL r0, r3
		ADD r6, r0, r2
		MOV r0, #0xaf
		STR r0, [sp, #0x120]
		MOV r0, #0x58
		STR r0, [sp, #0x124]
		LDR r0, [sp, #0x118]
		BL       |loc_080135D2|
		LDRB r2, [r6, #0x15]
		CMP r0, r2
		BLT      |loc_0801DAF6|
		MOV r0, #0x43
		B        |loc_0801DAF8|
|loc_0801DAF6|
		MOV r0, #0x44
|loc_0801DAF8|
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, sp, #0x11c
		BL       |sub_0803DC96|
		LDR r0, [r4, #0x3c]
		LDR r2, [r4, #0x38]
		SUB r1, r0, #3
		CMP r2, r1
		BGE      |loc_0801DB0E|
		STR r1, [r4, #0x38]
|loc_0801DB0E|
		LDR r1, [r4, #0x38]
		CMP r0, r1
		BGE      |loc_0801DB16|
		STR r0, [r4, #0x38]
|loc_0801DB16|
		MOV r6, #0
|loc_0801DB18|
		LDR r0, [r4, #0x38]
		LDR r2, [sp, #0x154]
		ADD r0, r0, r6
		LDR r1, [r2]
		CMP r1, r0
		BLE      |loc_0801DC06|
		LDR r2, [sp, #0x154]
		LSL r1, r0, #3
		ADD r7, r1, r2
		ADD r7, #4
		LDR r1, [r7]
		MOV r3, #0x2c
		LSL r1, r1, #4
		LSR r1, r1, #4
		LDR r2, [pc, #0x13c]
		MUL r1, r3
		ADD r5, r1, r2
		LDR r1, [r4, #0x3c]
		CMP r1, r0
		BNE      |loc_0801DB7A|
		MOV r0, #2
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
		MOV r0, #0x13
		STR r0, [sp, #0x120]
		MOV r0, #0x6a
		STR r0, [sp, #0x124]
		MOV r0, #0xc
		STRB r0, [r3, #0x1d]
		LDRH r0, [r5, #2]
		LDR r1, [pc, #0x110]
		LSL r0, r0, #2
		LDR r2, [r1, r0]
		MOV r1, #0xcc
		ADD r0, sp, #0x11c
		BL       |loc_0803DD66|
		LDR r0, [sp, #0x118]
		BL       |loc_080135D2|
		LDRB r1, [r5, #0x15]
		CMP r0, r1
		BLT      |loc_0801DB72|
		MOV r0, #6
		B        |loc_0801DB74|
|loc_0801DB72|
		MOV r0, #0x75
|loc_0801DB74|
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
		B        |loc_0801DB90|
|loc_0801DB7A|
		LDR r0, [sp, #0x118]
		BL       |loc_080135D2|
		LDRB r1, [r5, #0x15]
		CMP r0, r1
		BLT      |loc_0801DB8A|
		MOV r0, #2
		B        |loc_0801DB8C|
|loc_0801DB8A|
		MOV r0, #0x75
|loc_0801DB8C|
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
|loc_0801DB90|
		LSL r0, r6, #4
		STR r0, [sp, #0x150]
		ADD r0, #0x1c
		STR r0, [sp, #0x10c]
		MOV r0, #0x20
		STR r0, [sp, #0x110]
		LDR r0, [sp, #0x10c]
		MOV r1, #0x10
		ADD r0, r0, r1
		STR r1, [sp, #0x108]
		STR r0, [sp, #0x114]
		LDR r0, [r5, #0x10]
		ADD r1, sp, #8
		BL       |inc_0x03d784_0x041118| + 0x1bc
		ADD r2, sp, #0x108
		ADD r1, sp, #8
		ADD r0, sp, #0x11c
		BL       |inc_0x03d784_0x041118| + 0x219e
		LDR r0, [sp, #0x150]
		MOV r1, #0x22
		ADD r0, #0x28
		STR r0, [sp, #0x124]
		STR r1, [sp, #0x120]
		LDR r0, [r7]
		LSR r0, r0, #0x1c
		LDRH r0, [r5]
		BEQ      |loc_0801DC08|
		LDR r5, [pc, #0x9c]
		LSL r0, r0, #2
		LDR r0, [r5, r0]
		STR r0, [sp, #4]
		MOV r0, #0xff
		ADD r0, #0x15
		LDR r1, [r5, r0]
		LDR r0, [sp, #0x128]
		BL       |sub_0803FFE8|
		MOV r1, #0x7a
		SUB r1, r1, r0
		ADD r0, sp, #0x11c
		LDR r2, [sp, #4]
		BL       |loc_0803DCC4|
		LDR r0, [r7]
		LDR r1, [pc, #0x88]
		LSR r0, r0, #0x1c
		SUB r0, #1
		LDRB r0, [r1, r0]
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
		MOV r0, #0xff
		ADD r0, #0x15
		LDR r1, [r5, r0]
		ADD r0, sp, #0x11c
		BL       |loc_0803DADA|
		B        |loc_0801DC16|
|loc_0801DC06|
		DCW     0xE01F
|loc_0801DC08|
		LDR r1, [pc, #0x5c]
		LSL r0, r0, #2
		LDR r2, [r1, r0]
		MOV r1, #0x7a
		ADD r0, sp, #0x11c
		BL       |loc_0803DCC4|
|loc_0801DC16|
		ADD r6, #1
		CMP r6, #4
		BGE      |loc_0801DC1E|
		B        |loc_0801DB18|
|loc_0801DC1E|
		DCW     0xE013
