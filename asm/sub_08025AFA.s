	CODE16
|sub_08025AFA|
	LSR      r4, r0, #0x20
	MOV      r2, #3
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_08026B4C|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0x2e0]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xc]
	SUB      r1, #0xff
	SUB      r1, #0x44
	STRH     r1, [r0]
	ADD      sp, #0xec
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_08025B32|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08025B32|
	POP      {r3, pc}
|sub_08025B34|
|unk_08025B34|
; cited by 0x004C31D0 (a pool word names 0x08025C00)
		PUSH {r0, r4, r5, r6, r7, lr}
		SUB sp, #0x40
		LDR r1, [sp, #0x40]
		MOV r0, #1
		LSL r0, r0, #0xf
		ADD r0, r1, r0
		LDR r1, [r0, #0x2c]
		LDR r0, [r0, #0x30]
		SUB r1, #8
		LSL r2, r1, #0x18
		LSR r6, r2, #0x1b
		SUB r0, #0x30
		LSL r2, r0, #0x18
		ASR r0, r0, #8
		STR r0, [sp, #0xc]
		MOV r0, #0x20
		SUB r0, r0, r6
		STR r0, [sp, #8]
		LDR r0, [sp, #0xc]
		ASR r1, r1, #8
		LSR r5, r2, #0x1b
		CMP r0, #0
		STR r1, [sp, #0x10]
		LDR r4, [pc, #0x290]
		BGE      |loc_08025B80|
		ADD r7, r5, #0
		CMP r5, #0x20
		BGE      |loc_08025C12|
|loc_08025B6C|
		LSL r0, r7, #6
		ADD r0, r0, r4
		MOV r2, #0x40
		MOV r1, #0
		BL       |sub_0804912C|
		ADD r7, #1
		CMP r7, #0x20
		BLT      |loc_08025B6C|
		B        |loc_08025C12|
|loc_08025B80|
		LDR r1, [sp, #0x10]
		CMP r1, #0
		BGE      |loc_08025BAE|
		ADD r7, r5, #0
		CMP r5, #0x20
		BGE      |loc_08025BEC|
		LDR r0, [sp, #8]
		LSL r2, r0, #1
		LSL r1, r6, #1
		STR r1, [sp, #0x38]
		STR r2, [sp, #0x3c]
|loc_08025B96|
		LSL r0, r7, #6
		LDR r1, [sp, #0x38]
		ADD r0, r0, r4
		ADD r0, r0, r1
		MOV r1, #0
		LDR r2, [sp, #0x3c]
		BL       |sub_08049168|
		ADD r7, #1
		CMP r7, #0x20
		BLT      |loc_08025B96|
		B        |loc_08025BEC|
|loc_08025BAE|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #0xd
		ADD r0, r0, r1
		LDR r1, [sp, #0x10]
		ADD r7, r5, #0
		LSL r1, r1, #6
		ADD r1, r0, r1
		ADD r1, #0xc
		STR r1, [sp, #4]
		CMP r5, #0x20
		BGE      |loc_08025BEC|
		LDR r0, [sp, #8]
		LSL r0, r0, #1
		LSL r2, r6, #1
		STR r2, [sp, #0x30]
		STR r0, [sp, #0x34]
|loc_08025BD0|
		LDR r1, [sp, #4]
		LSL r0, r7, #8
		LDR r2, [sp, #0x30]
		ADD r0, r0, r1
		ADD r1, r0, r2
		LSL r0, r7, #6
		ADD r0, r0, r4
		ADD r0, r0, r2
		LDR r2, [sp, #0x34]
		BL       |Thunk_PaletteCopy|
		ADD r7, #1
		CMP r7, #0x20
		BLT      |loc_08025BD0|
|loc_08025BEC|
		CMP r6, #0
		BEQ      |loc_08025C12|
		LDR r1, [sp, #0x10]
		CMP r1, #3
		BLT      |sub_08025C14|
		ADD r7, r5, #0
		CMP r5, #0x20
		BGE      |loc_08025C12|
		LSL r2, r6, #1
		STR r2, [sp, #0x2c]
|loc_08025C00|
		LSL r0, r7, #6
		ADD r0, r0, r4
		MOV r1, #0
		LDR r2, [sp, #0x2c]
		BL       |sub_08049168|
		ADD r7, #1
		CMP r7, #0x20
		BLT      |loc_08025C00|
|loc_08025C12|
		B        |loc_08025C46|
