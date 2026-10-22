	CODE16
|sub_0802C12E|
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x6c]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x68]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_0802C14C|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_0802C14C|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x4c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x48]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0802C178|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802C178|
	ADD      sp, #0x10
	POP      {r4, pc}
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x24]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0802C18A|
	MOV      r0, #0
|loc_0802C18A|
	SUB      r0, r2, r0
	BX       lr
	LDR      r0, [pc, #0x18]
	ADD      r0, #4
	BX       lr
	LDR      r0, [pc, #0x3a0]
	LSR      r5, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	ADD      r0, #0x74
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r0, [r4, #0x50]
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x2348
	STRB     r0, [r4, #0x11]
	ADD      r0, r4, #0
	LDR      r1, [pc, #8]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
|sub_0802C1D0|
|unk_0802C1D0|
; cited by 0x0802C1C8 (a pc-relative load targets 0x0802C1D4)
	INCBIN  baserom.gba_0x2c1d0_0x2c1dc.extracted
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r1, #0
		ADD r0, r1, #0
		LDR r1, [r1]
		SUB sp, #0x3c
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		ADD r7, r4, #0
		ADD r7, #0xff
		ADD r7, #0xa1
		MOV r5, #0
		ADD r6, r7, #4
|loc_0802C1FA|
		ADD r1, sp, #0x2c
|loc_0802C1FC|
		MOV r0, #0xc9
		BL       |inc_0x03d784_0x041118| + 0x2348
		SUB r0, #0x64
		LSL r0, r0, #8
		STR r0, [sp, #0x34]
		MOV r0, #0xc9
		BL       |inc_0x03d784_0x041118| + 0x2348
		SUB r0, #0x64
		LSL r0, r0, #8
		STR r0, [sp, #0x38]
		LDR r0, [r7]
		LDR r1, [sp, #0x34]
		ADD r0, r0, r1
		LDR r1, [r6]
		LDR r2, [sp, #0x38]
		STR r0, [sp, #0x1c]
		ADD r1, r1, r2
		STR r1, [sp, #0x20]
		STR r1, [sp, #0x28]
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x24]
		STR r0, [sp, #0x2c]
		LDR r0, [sp, #0x34]
		LDR r1, [pc, #0x110]
		CMP r0, r1
		BLE      |loc_0802C248|
		LDR r0, [sp, #0x34]
		NEG r2, r1
		CMP r0, r2
		BGE      |loc_0802C248|
		LDR r0, [sp, #0x38]
		CMP r0, r1
		BLE      |loc_0802C248|
		LDR r0, [sp, #0x38]
		CMP r0, r2
		BLT      |loc_0802C1FC|
|loc_0802C248|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x2c
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0802C320|
		LDR r0, [pc, #0xe8]
		LDR r0, [r0]
		BL       |loc_080116FC|
		MOV r5, #1
		LSL r5, r5, #0xa
		CMP r0, r5
		BLT      |loc_0802C2BA|
		LSL r0, r5, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		LSL r1, r5, #2
		ADD r0, r0, r1
		STR r0, [sp, #0x10]
		ADD r0, sp, #0x14
		ADD r1, r4, #0
		BL       |loc_0800FE34|
		LDR r0, [sp, #0x14]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x20]
		ADD r1, r0, r1
		STR r1, [sp, #8]
		ASR r1, r1, #1
		LDR r0, [sp, #0x18]
		STR r1, [sp, #8]
		ADD r0, r0, r2
		STR r0, [sp, #0xc]
		ASR r0, r0, #1
		STR r0, [sp, #0x28]
		STR r0, [sp, #0xc]
		LDR r0, [sp, #0x10]
		MOV r2, #0x37
		STR r1, [sp, #0x24]
		STR r2, [sp, #8]
		MOV r3, #4
		STR r0, [sp]
		MOV r0, #0
		LDR r2, [pc, #0xa0]
		STR r5, [sp, #4]
		ADD r1, sp, #0x24
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [pc, #0x90]
		LDR r0, [r0]
		BL       |List_Append|
|loc_0802C2BA|
		LDR r0, [sp, #0x2c]
		STR r0, [r7]
		LDR r0, [sp, #0x30]
		STR r0, [r6]
		LDR r6, [pc, #0x80]
		LDR r0, [r6]
		BL       |loc_080116FC|
		CMP r0, r5
		BLT      |sub_0802C328|
		MOV r7, #1
		LSL r7, r7, #0xc
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r7, r0, r7
		ADD r0, sp, #0x14
		ADD r1, r4, #0
		BL       |loc_0800FE34|
		LDR r0, [sp, #0x14]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x20]
		ADD r1, r0, r1
		LDR r0, [sp, #0x18]
