	CODE16
|sub_0803BF06|
	MOV      r0, #0
	MOV      r1, #1
	SUB      r0, r1, r0
	BX       lr
|sub_0803BF0E|
|unk_0803BF0E|
; cited by 0x0803BDA6 (a pc-relative load targets 0x0803BF14)
	INCBIN  baserom.gba_0x3bf0e_0x3bf28.extracted
		PUSH {r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		ADD r4, r1, #0
		MOV r0, #2
		SUB sp, #0x1c
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r1, r0, #0
		LDR r0, [pc, #0x16c]
		LDR r1, [r0]
		BNE      |loc_0803BF44|
		SUB r1, #1
		STR r1, [r0]
		B        |loc_0803BF48|
|loc_0803BF44|
		ADD r1, #1
		STR r1, [r0]
|loc_0803BF48|
		LDR r1, [r0]
		CMP r1, #0
		BGE      |loc_0803BF54|
		MOV r1, #4
		STR r1, [r0]
		B        |loc_0803BF5C|
|loc_0803BF54|
		CMP r1, #4
		BLE      |loc_0803BF5C|
		MOV r1, #0
		STR r1, [r0]
|loc_0803BF5C|
		LDR r0, [r0]
		LDR r1, [pc, #0x14c]
		LSL r0, r0, #3
		ADD r0, r0, r1
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0xa1
		LDMIA r0!, {r2}
		LDMIA r1!, {r3}
		LDR r0, [r0]
		LDR r1, [r1]
		SUB r2, r2, r3
		ADD r6, r5, #4
		SUB r0, r0, r1
		STR r0, [sp, #8]
		LDR r1, [sp, #8]
		MOV r0, #0xf
		STR r1, [sp, #0x10]
		LSL r1, r2, #8
		LSL r0, r0, #0xa
		STR r2, [sp, #4]
		STR r2, [sp, #0xc]
		BL       |sub_08046E58|
		ADD r7, r0, #0
		LDR r0, [sp, #0x10]
		LSL r1, r0, #8
		MOV r0, #0xf
		LSL r0, r0, #0xa
		BL       |sub_08046E58|
		STR r0, [sp, #8]
		LDR r1, [sp, #8]
		STR r7, [sp, #4]
		STR r7, [sp, #0x14]
		STR r1, [sp, #0x18]
		STR r7, [r6]
		LDR r1, [sp, #0x18]
		MOV r0, #0x3c
		STR r1, [r6, #4]
		STR r0, [r5, #0xc]
		LDR r0, [pc, #0xf8]
		MOV r1, #1
		LSL r1, r1, #9
		LDR r0, [r0]
		ADD r1, r4, r1
		STR r0, [r1, #0x14]
		MOV r0, #0x24
		STRB r0, [r4, #8]
		LDR r0, [r5, #4]
		CMP r0, #0
		BLT      |loc_0803BFC8|
		ADD r1, r0, #0
		B        |loc_0803BFCA|
|loc_0803BFC8|
		NEG r1, r0
|loc_0803BFCA|
		LDR r2, [r5, #8]
		CMP r2, #0
		BLT      |sub_0803BFD4|
		ADD r3, r2, #0
		B        |inc_0x351c0_0x3d4d0| + 0x6e16
|sub_0803BFD4|
|unk_0803BFD4|
		NEG r3, r2
	CMP      r1, r3
	BLT      |loc_0803BFEC|
	CMP      r0, #0
	BLE      |sub_0803BFE6|
	MOV      r0, #3
	STRB     r0, [r4, #0x10]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
