	IMPORT |GBARam_Malloc|
	CODE16
	EXPORT |sub_0802BB4C|
	EXPORT |loc_0802BB7C|
	EXPORT |loc_0802BBFA|
	EXPORT |sub_0802BC1A|
	EXPORT |sub_0802BC40|
	EXPORT |loc_0802BC64|
	EXPORT |sub_0802BCCE|
	EXPORT |sub_0802BD04|
	EXPORT |sub_0802BD20|
	EXPORT |sub_0802BD32|
	EXPORT |sub_0802BD36|
	EXPORT |loc_0802BD3C|
	EXPORT |loc_0802BD4C|
	EXPORT |sub_0802BD6A|
	EXPORT |sub_0802BD90|
	EXPORT |sub_0802BDAA|
	EXPORT |sub_0802BDBE|
	EXPORT |loc_0802BDE6|
	EXPORT |loc_0802BE8A|
	EXPORT |sub_0802BEC4|
	EXPORT |sub_0802BECC|
	EXPORT |sub_0802BEEA|
	EXPORT |sub_0802BFBC|
	EXPORT |loc_0802BFFE|
	EXPORT |loc_0802C038|
	EXPORT |sub_0802C054|
	EXPORT |sub_0802C066|
	EXPORT |sub_0802C0B0|
	EXPORT |sub_0802C12E|
	EXPORT |loc_0802C14C|
	EXPORT |loc_0802C178|
	EXPORT |loc_0802C18A|
	EXPORT |sub_0802C1D0|
	EXPORT |loc_0802C2EC|
	EXPORT |sub_0802C328|
	EXPORT |sub_0802C33C|
	EXPORT |sub_0802C340|
	EXPORT |loc_0802C3BA|
	EXPORT |loc_0802C3CE|
	EXPORT |sub_0802C3E6|
	EXPORT |loc_0802C400|
	EXPORT |sub_0802C446|
	EXPORT |loc_0802C456|
	EXPORT |loc_0802C482|
	EXPORT |loc_0802C4AE|
	EXPORT |sub_0802C4B8|
	EXPORT |sub_0802C4BA|
	EXPORT |loc_0802C4FA|
	EXPORT |sub_0802C5BA|
	EXPORT |sub_0802C630|
	EXPORT |sub_0802C640|
	EXPORT |sub_0802C644|
	EXPORT |loc_0802C64E|
	EXPORT |sub_0802C668|
	EXPORT |loc_0802C66A|
	EXPORT |loc_0802C66E|
	EXPORT |sub_0802C672|
	EXPORT |loc_0802C682|
	EXPORT |sub_0802C684|
	EXPORT |sub_0802C686|
	EXPORT |sub_0802C6B0|
	EXPORT |sub_0802C6EC|
	EXPORT |sub_0802C6FE|
	EXPORT |sub_0802C782|
	EXPORT |sub_0802C7AC|
	EXPORT |sub_0802C7EA|
	EXPORT |loc_0802C85C|
	EXPORT |sub_0802C868|
	EXPORT |sub_0802C8AE|
	EXPORT |sub_0802C8BE|
	EXPORT |loc_0802C8F4|
	EXPORT |sub_0802C8FE|
	EXPORT |Mosaic_WriteSize1|
	EXPORT |sub_0802C98E|
	EXPORT |loc_0802CA1A|
	EXPORT |Mosaic_WriteSize2|
	EXPORT |Bg_WriteControl0AndMosaic2|
	EXPORT |loc_0802CAA0|
	EXPORT |sub_0802CAF8|
	EXPORT |sub_0802CAFA|
	EXPORT |loc_0802CB3A|
	EXPORT |loc_0802CB42|
	EXPORT |sub_0802CB4E|
	EXPORT |sub_0802CB52|
	EXPORT |loc_0802CB64|
	EXPORT |loc_0802CB90|
	EXPORT |sub_0802CBAA|
	EXPORT |sub_0802CBAE|
	EXPORT |loc_0802CD0E|
	EXPORT |sub_0802CD10|
	EXPORT |sub_0802CD12|
	EXPORT |loc_0802CD40|
	EXPORT |sub_0802CD42|
	EXPORT |sub_0802CD78|
	EXPORT |sub_0802CD80|
	EXPORT |sub_0802CD82|
	EXPORT |loc_0802CDA4|
	EXPORT |sub_0802CDA6|
	EXPORT |sub_0802CDE4|
	EXPORT |loc_0802CDFA|
	EXPORT |sub_0802CE00|
	EXPORT |sub_0802D08C|
	EXPORT |loc_0802D0A8|
	EXPORT |loc_0802D0DA|
	EXPORT |sub_0802D102|
	EXPORT |sub_0802D168|
	EXPORT |loc_0802D18A|
	EXPORT |loc_0802D1B6|
	EXPORT |sub_0802D1BA|
|sub_0802BB4C|
	LSL      r0, r6, #2
	LDR      r1, [pc, #0xb0]
	ADD      r0, r0, r6
	LSL      r0, r0, #2
	SUB      r1, #0x64
	ADD      r5, r0, r1
	ADD      r0, r7, r6
	LDRB     r1, [r0, #0x15]
	LDRB     r2, [r0, #0x10]
	CMP      r1, r2
	BEQ      |loc_0802BB7C|
	STRB     r1, [r0, #0x10]
	LDRH     r0, [r7, #0xc]
	LDR      r2, [pc, #0x94]
	LSL      r0, r0, #5
	ADD      r0, r0, r2
	LDR      r2, [r5]
	ADD      r0, r0, r2
	LDR      r2, [r5, #8]
	LDR      r3, [r5, #4]
	MUL      r1, r2
	ADD      r1, r1, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0802BB7C|
	LDR      r0, [r5, #0x10]
	LDR      r2, [pc, #0x98]
	STR      r0, [r4]
	LDRB     r1, [r5, #0xc]
	AND      r0, r2
	ADD      r6, #1
	ADD      r1, #8
	LSL      r1, r1, #0x10
	ORR      r0, r1
	STR      r0, [r4]
	LDRB     r1, [r5, #0xd]
	LSR      r0, r0, #8
	LSL      r0, r0, #8
	ADD      r1, #8
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	ORR      r0, r1
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	MOV      r1, #3
	LSL      r1, r1, #0xa
	BIC      r0, r1
	MOV      r1, #1
	LSL      r1, r1, #0xa
	ADD      r0, r0, r1
	STR      r0, [r4, #4]
	LDRH     r1, [r7, #0xc]
	LDR      r2, [r5]
	LSR      r0, r0, #0xa
	ASR      r2, r2, #5
	ADD      r1, r1, r2
	LSL      r1, r1, #0x16
	LSR      r1, r1, #0x16
	LSL      r0, r0, #0xa
	ORR      r0, r1
	STR      r0, [r4, #4]
	ADD      r4, #8
	CMP      r6, #5
	BLT      |sub_0802BB4C|
	LDR      r0, [pc, #0x50]
	MOV      r1, #3
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	LSL      r1, r1, #0xa
	BIC      r0, r1
	MOV      r1, #1
	LSL      r1, r1, #0xa
	ADD      r0, r0, r1
	STR      r0, [r4, #4]
	LDRH     r1, [r7, #0xc]
	LSR      r0, r0, #0xa
	LSL      r0, r0, #0xa
	LSL      r1, r1, #0x16
	LSR      r1, r1, #0x16
	ORR      r0, r1
	STR      r0, [r4, #4]
	ADD      r0, r4, #0
	LDR      r1, [sp, #8]
	ADD      r0, #8
	STR      r0, [r1]
	ADD      sp, #0xc
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
|loc_0802BBFA|
	DCW      0x0000
	DCW      0x0000,0x0601,0x3008,0x0875,0x9680,0x0804,0xb400,0x0804
	DCW      0xffff,0x7fff,0x0271,0x0000,0xf424,0x0000,0xffff
|sub_0802BC1A|
|unk_0802BC1A|
	INCBIN	baserom.gba_0x2bc1a_0x2bc1e.extracted
	STRH     r0, [r1]
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BEQ      |sub_0802BC40|
	CMP      r1, #0x1b
	BNE      |loc_0802BC64|
	ADD      r0, #0x1c
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #3
	ADD      r0, r1, r0
	ADD      r0, #4
	LDMIA    r2!, {r1, r2}
	STMIA    r0!, {r1, r2}
	MOV      r0, #1
	POP      {r3, pc}
|sub_0802BC40|
|unk_0802BC40|
		MOV r1, #0
		MOV r2, #0xff
|loc_0802BC44|
		ADD r3, r0, r1
		ADD r1, #1
		CMP r1, #5
		STRB r2, [r3, #0x10]
		BLT      |loc_0802BC44|
		LDRH r0, [r0, #0xc]
		LDR r1, [pc, #0x14]
		MOV r2, #1
		LSL r0, r0, #5
		ADD r0, r0, r1
		LDR r1, [pc, #0x10]
		LSL r2, r2, #0xa
		BL       |Thunk_VramCopy|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xf2
|loc_0802BC64|
|unk_0802BC64|
; cited by 0x0802BC50 (a pc-relative load targets 0x0802BC68)
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xf2
		DCD     0x06010000
		DCD     0x08753008
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r1, #0
		MOV r1, #0x87
		LDR r6, [pc, #0xc0]
		LDR r2, [pc, #0xc0]
		LSL r1, r1, #2
		ADD r5, r0, #0
		LDR r0, [r6]
		ADD r1, r1, r2
		LDR r7, [pc, #0xbc]
		MOV r2, #0x40
		MOV r3, #0
		ADD r0, r0, r7
		SUB sp, #0x1c
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r4, [r4, #4]
		LDR r0, [r4, #0x14]
		LDR r1, [r0]
		LDR r2, [r1, #0x14]
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		STR r0, [r5, #0x10]
		CMP r0, #0
		BEQ      |loc_0802BCAA|
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xf3e4
|loc_0802BCAA|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x30]
		ADD r3, r2, r1
		MOV r2, #1
		MOV r1, #0xd
		BL       |inc_0x042118_0x049114| + 0x498e
		LDR r0, [r5, #0xc]
		CMP r0, #0
		BGE      |sub_0802BCCE|
		NEG r0, r0
		MOV r3, #0x2c
		LDR r1, [pc, #0x7c]
		MUL r0, r3
		ADD r5, r0, r1
		ADD r5, #4
		B        |inc_0x2bb4c_0x2d1c0| + 0x18c
|sub_0802BCCE|
	MOV      r3, #0x34
	LDR      r1, [pc, #0x74]
	MUL      r0, r3
	ADD      r5, r0, r1
	ADD      r5, #0xc
	ADD      r1, r4, #0
	ADD      r0, sp, #0xc
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	ADD      r2, sp, #4
	ADD      r0, r0, r1
	ASR      r0, r0, #1
	STR      r0, [sp, #4]
	LDR      r0, [sp, #0x10]
	ADD      r1, r5, #0
	STR      r0, [sp, #8]
	MOV      r0, #0
	BL       |loc_0802BD4C|
	ADD      r1, r0, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_0802BD04|
|unk_0802BD04|
		PUSH {r3, lr}
		LDR r2, [r0, #8]
		ADD r2, #1
		STR r2, [r0, #8]
		CMP r2, #0x3c
		BLT      |sub_0802BD32|
		LDR r1, [r1, #4]
		LDR r0, [r0, #0x10]
		CMP r0, #0
		BEQ      |sub_0802BD20|
		ADD r0, r1, #0
		BL       |inc_0x0158_0x143f2| + 0xf400
		B        |inc_0x2bb4c_0x2d1c0| + 0x1e2
|sub_0802BD20|
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	POP      {r3, pc}
|sub_0802BD32|
|unk_0802BD32|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x1e4
|sub_0802BD36|
	LSL      r0, r0, #0
	SUB      r2, #8
	LSR      r5, r6, #1
|loc_0802BD3C|
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	BCS      |loc_0802BD3C|
	LSR      r3, r7, #0x20
|loc_0802BD4C|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #8
	BNE      |sub_0802BD6A|
	MOV      r0, #0x34
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802BD6A|
	ADD      r0, r4, #0
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
|sub_0802BD6A|
|unk_0802BD6A|
		ADD r2, r6, #0
		MOV r6, sp
		ADD r1, r5, #0
		MOV r0, sp
		BL       |inc_0x0158_0x143f2| + 0xd8ce
		ADD r2, r6, #0
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800D960|
		LDR r0, [pc, #0x40]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0x30]
		MOV r0, #0x28
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x21a
|sub_0802BD90|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x30]
	ADD      r1, #1
	STR      r1, [r0, #0x30]
	CMP      r1, #0x3c
	BLE      |sub_0802BDAA|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x28]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #0
	POP      {r3, pc}
|sub_0802BDAA|
|unk_0802BDAA|
		MOV r2, #0xf
		BIC r2, r1
		DCW     0xD105
		LDR r1, [r0, #0x1c]
		SUB r1, #1
		STR r1, [r0, #0x1c]
		LDR r1, [r0, #0x24]
		SUB r1, #1
		STR r1, [r0, #0x24]
	INCBIN  baserom.gba_0x2bdbc_0x2bdbe.extracted
|sub_0802BDBE|
|unk_0802BDBE|
	INCBIN	baserom.gba_0x2bdbe_0x2bdc2.extracted
	LSL      r0, r0, #0
|unk_0802BDC4|
	INCBIN	baserom.gba_0x2bdc4_0x2bdc6.extracted
	LSR      r4, r0, #0x20
	SUB      r2, #0x10
	LSR      r5, r6, #1
	LDR      r2, [pc, #0x20]
	LDR      r1, [r1, #4]
	LDR      r2, [r2]
	ADD      r2, #0x80
	LDR      r2, [r2, #0x10]
	LDR      r0, [r0, #8]
	LSL      r0, r0, #0xa
	CMP      r2, #0
	BEQ      |loc_0802BDE6|
	ADD      r1, #0xff
	ADD      r1, #0xad
	STR      r0, [r1]
	BX       lr
|loc_0802BDE6|
	ADD      r1, #0xff
	ADD      r1, #0x81
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	SUB      r2, #0x14
	LSR      r5, r6, #1
	PUSH     {r4, r5}
	LDR      r2, [r1, #4]
	SUB      sp, #8
	ADD      r2, #0x24
	LDR      r4, [r2, #8]
	LDR      r5, [r2]
	LDR      r1, [r2, #0xc]
	SUB      r4, r4, r5
	LDR      r5, [r2, #4]
	STR      r4, [sp]
	SUB      r1, r1, r5
	STR      r1, [sp, #4]
	ADD      r1, r4, #0
	ADD      r3, r0, #0
	ADD      r3, #0x10
	LDR      r4, [sp, #4]
	STMIA    r3!, {r1, r4}
	LDR      r1, [r0, #8]
	LDR      r3, [r2]
	SUB      r1, r1, r3
	LDR      r3, [r0, #0xc]
	LDR      r4, [r2, #4]
	STR      r1, [sp]
	SUB      r3, r3, r4
	STR      r3, [sp, #4]
	LDR      r4, [r2]
	LDR      r2, [r2, #4]
	ADD      r5, r1, #0
	LSL      r2, r2, #8
	STR      r2, [r0, #0x24]
	LSL      r4, r4, #8
	STR      r4, [r0, #0x20]
	MOV      r2, #0x2c
	STR      r2, [r0, #0x28]
	LDR      r2, [pc, #0x88]
	ADD      r1, r3, #0
	LDR      r3, [pc, #0x84]
	MUL      r2, r5
	ASR      r2, r2, #8
	STR      r2, [r0, #0x18]
	LDR      r2, [pc, #0x80]
	MUL      r1, r3
	ADD      r1, r1, r2
	MOV      r2, #1
	LSL      r2, r2, #9
	ASR      r1, r1, #8
	SUB      r1, r1, r2
	STR      r1, [r0, #0x1c]
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
	PUSH     {r4, r5}
	LDR      r2, [r0, #0x1c]
	SUB      sp, #8
	ADD      r2, #0x20
	STR      r2, [r0, #0x1c]
	LDR      r3, [r0, #0x20]
	LDR      r4, [r0, #0x18]
	ADD      r3, r3, r4
	STR      r3, [r0, #0x20]
	LDR      r3, [r0, #0x24]
	ADD      r2, r3, r2
	STR      r2, [r0, #0x24]
	LDR      r2, [r0, #0x28]
	SUB      r2, #1
	STR      r2, [r0, #0x28]
	BNE      |loc_0802BE8A|
	LDR      r3, [r0, #8]
	LDR      r4, [r0, #0xc]
	LSL      r3, r3, #8
	LSL      r4, r4, #8
	MOV      r2, #1
	STR      r2, [r0, #0x2c]
	STR      r3, [r0, #0x20]
	STR      r4, [r0, #0x24]
|loc_0802BE8A|
	LDR      r1, [r1, #4]
	LDR      r3, [r0, #0x20]
	LDR      r4, [r0, #0x24]
	ASR      r3, r3, #8
	STR      r3, [r1, #0x24]
	ASR      r4, r4, #8
	STR      r4, [r1, #0x28]
	ADD      r2, r1, #0
	ADD      r2, #0x24
	ADD      r3, r2, #0
	LDR      r2, [r2, #4]
	LDR      r4, [r1, #0x24]
	LDR      r5, [r0, #0x10]
	LDR      r0, [r0, #0x14]
	ADD      r4, r4, r5
	ADD      r0, r2, r0
	STR      r0, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r4, [sp]
	ADD      r3, #8
	STR      r2, [r3, #4]
	STR      r4, [r3]
	LDR      r0, [r1, #0x30]
	LDR      r2, [r1, #0x18]
	ADD      r0, r0, r2
	STR      r0, [r1, #4]
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
|sub_0802BEC4|
	DCW      0x05d3
	DCW      0x0000,0x45a0,0xffff
|sub_0802BECC|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x44
	BNE      |sub_0802BEEA|
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802BEEA|
	ADD      r0, r4, #0
	ADD      sp, #0x54
	POP      {r4, r5, r6, r7, pc}
|sub_0802BEEA|
|unk_0802BEEA|
		LDR r0, [pc, #0x16c]
		LSL r5, r6, #5
		STR r0, [r4]
		LDR r0, [pc, #0x168]
		STRH r5, [r4, #0xe]
		LDR r0, [r0]
		ADD r1, r5, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0802BF14|
		LDR r0, [pc, #0x158]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |sub_08011732|
		LDR r0, [pc, #0x150]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |loc_0801124C|
|loc_0802BF14|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x148]
		ADD r1, r6, #0
		STR r0, [r4]
		MOV r2, #0x20
		ADD r5, sp, #0x10
		ADD r0, r5, #0
		STR r6, [r4, #0x10]
		BL       |loc_0803F540|
		LDR r0, [pc, #0x130]
		ADD r3, sp, #0
		LDR r0, [r0, #4]
		MOV r1, #2
		STR r0, [sp, #0x1c]
		MOV r0, #1
		STRB r0, [r3, #0x10]
		STRB r1, [r3, #0x13]
		STRB r0, [r3, #0x12]
		LDR r0, [pc, #0x128]
		STR r0, [sp, #0x30]
		LDR r0, [r4, #0x10]
		LDR r2, [sp, #0x40]
		LSR r1, r0, #0x1f
		ADD r0, r1, r0
		ASR r0, r0, #1
		STR r0, [sp, #0x14]
		MOV r0, #0x16
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x34]
		MOV r1, #0
		BL       |sub_08046E40|
		ADD r0, r5, #0
		LDR r1, [sp, #0x4c]
		BL       |loc_0803DADA|
		LDR r0, [r4, #0x10]
		LSR r1, r0, #0x1f
		ADD r0, r1, r0
		LDR r1, [r7]
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [r4, #0x14]
		LDR r0, [r7, #4]
		SUB r0, #0x10
		STR r0, [r4, #0x18]
		MOV r0, #0
		STR r0, [sp, #4]
		MOV r0, #0x20
		STR r0, [sp, #0xc]
		LDR r1, [r4, #0x10]
		MOV r0, #0
		CMP r1, #0
		BLE      |loc_0802BFAA|
		MOV r6, sp
		ADD r7, sp, #0x10
|loc_0802BF86|
		ADD r5, r0, #0
		ADD r5, #0x20
		STR r5, [sp, #8]
		STR r0, [sp]
		LDRH r1, [r4, #0xc]
		LDR r2, [pc, #0xd4]
		LSL r0, r0, #5
		LSL r1, r1, #5
		ADD r1, r1, r2
		ADD r1, r1, r0
		ADD r2, r6, #0
		ADD r0, r7, #0
		BL       |sub_0804915C|
		LDR r1, [r4, #0x10]
		ADD r0, r5, #0
		CMP r1, r5
		BGT      |loc_0802BF86|
|loc_0802BFAA|
		MOV r0, #0
		STR r0, [r4, #4]
		STRB r0, [r4, #8]
		ADD r0, sp, #0x10
		MOV r1, #0
		BL       |sub_0803F58C|
		ADD r0, r4, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x39a
|sub_0802BFBC|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	LDR      r1, [pc, #0xa8]
	LSL      r0, r0, #2
	LDR      r4, [r1, r0]
	LDR      r6, [pc, #0x94]
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x03d784_0x041118| + 0x2864
	ADD      r0, #0x21
	LSR      r5, r0, #5
	LSL      r5, r5, #5
	LSL      r1, r5, #5
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r3, r7, #0
	ADD      r2, r4, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |sub_0802BECC|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7}
	LDR      r2, [r1]
	LDR      r4, [r0, #0x10]
	MOV      r3, #0
	CMP      r4, #0
	BLE      |loc_0802C038|
	MOV      r6, #3
	LDR      r7, [pc, #0x74]
	LSL      r6, r6, #0xa
|loc_0802BFFE|
	STR      r7, [r2]
	LDR      r4, [r0, #0x14]
	ADD      r4, r4, r3
	LSL      r4, r4, #0x17
	LSR      r4, r4, #7
	ORR      r4, r7
	STR      r4, [r2]
	LDR      r5, [r0, #0x18]
	LSR      r4, r4, #8
	LSL      r5, r5, #0x18
	LSR      r5, r5, #0x18
	LSL      r4, r4, #8
	ORR      r4, r5
	STR      r4, [r2]
	LDRH     r4, [r0, #0xc]
	LDR      r5, [r2, #4]
	ADD      r4, r4, r3
	LSL      r4, r4, #0x16
	LSR      r5, r5, #0xa
	LSL      r5, r5, #0xa
	LSR      r4, r4, #0x16
	ORR      r4, r5
	BIC      r4, r6
	STR      r4, [r2, #4]
	LDR      r4, [r0, #0x10]
	ADD      r2, #8
	ADD      r3, #0x20
	CMP      r4, r3
	BGT      |loc_0802BFFE|
|loc_0802C038|
	STR      r2, [r1]
	POP      {r4, r5, r6, r7}
	MOV      r0, #0
	BX       lr
	PUSH     {r3, lr}
	CMP      r1, #0x27
	BNE      |sub_0802C054|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x10]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #0
	POP      {r3, pc}
|sub_0802C054|
|unk_0802C054|
; cited by 0x0802BEEA (a pc-relative load targets 0x0802C058)
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x506
	INCBIN  baserom.gba_0x2c058_0x2c066.extracted
|sub_0802C066|
	LSR      r3, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	MOV      r0, #0
	STRH     r0, [r0]
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x13
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	BCC      |sub_0802C0B0|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
|sub_0802C0B0|
|unk_0802C0B0|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #8
		BNE      |inc_0x2bb4c_0x2d1c0| + 0x560
		LDR r5, [pc, #0xd8]
		LDR r0, [r5, #4]
		BL       |loc_080116FC|
		CMP r0, #0x80
		BLT      |inc_0x2bb4c_0x2d1c0| + 0x560
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xb0]
		ADD r1, #8
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		ADD r3, r4, #0
		MOV r0, #0
		LDRB r2, [r4, #0x10]
		ADD r1, sp, #0x14
		BL       |inc_0x2bb4c_0x2d1c0| + 0xc44
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |sub_0801191A|
		MOV r1, #0xb7
		LDR r2, [pc, #0x7c]
		LSL r1, r1, #2
		ADD r1, r1, r2
		LDR r4, [pc, #0x7c]
		LDR r0, [r5]
		MOV r2, #0x40
		MOV r3, #0
		ADD r0, r0, r4
		BL       |inc_0x03d784_0x041118| + 0xbf4
		B        |inc_0x2bb4c_0x2d1c0| + 0x560
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
		BL       |sub_0801191A|
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
|loc_0802C2EC|
|unk_0802C2EC|
		STR r1, [sp, #0xc]
		ADD r0, r0, r2
		STR r0, [sp, #0x10]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #0x24]
		STR r0, [sp, #0x28]
		MOV r2, #0x37
		STR r5, [sp, #4]
		STR r1, [sp, #0xc]
		STR r0, [sp, #0x10]
		ADD r3, sp, #0x24
		ADD r1, r3, #0
		MOV r0, #0
		MOV r5, #4
		STR r2, [sp, #8]
		LDR r2, [pc, #0x38]
		ADD r3, r5, #0
		STR r7, [sp]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [r6]
		BL       |sub_0801191A|
		B        |sub_0802C328|
|loc_0802C320|
		ADD r5, #1
		CMP r5, #0x10
		BGE      |sub_0802C328|
		B        |loc_0802C1FA|
|sub_0802C328|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_0802C33C|
|unk_0802C33C|
	INCBIN	baserom.gba_0x2c33c_0x2c340.extracted
|sub_0802C340|
	DCW      0xba00
	DCW      0xffff,0x4928
	LSR      r5, r6, #1
	BLS      |loc_0802C2EC|
	LSR      r7, r5, #1
	ADD      r0, #0x80
	LSL      r0, r0, #0xc
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r0, #4
	ADD      r2, #0xa1
	LDMIA    r2!, {r3}
	STMIA    r0!, {r3}
	LDR      r2, [r2]
	STR      r2, [r0]
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r6, r1, #0
	ADD      r4, r1, #0
	ADD      r0, #1
	SUB      sp, #0x18
	STRH     r0, [r1, #0x12]
	LSL      r0, r0, #0x1f
	BMI      |loc_0802C3BA|
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #1
	LSL      r0, r0, #8
	STR      r0, [sp, #0x10]
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #1
	LSL      r0, r0, #8
	STR      r0, [sp, #0x14]
	LDR      r2, [r5, #4]
	LDR      r3, [sp, #0x10]
	LDR      r1, [r5, #8]
	ADD      r2, r2, r3
	LDR      r3, [sp, #0x14]
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r1, r1, r3
	STR      r1, [sp, #4]
	ADD      r0, #0xa1
	ADD      r1, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	STMIA    r0!, {r1}
	LDR      r1, [sp, #0xc]
	STR      r1, [r0]
|loc_0802C3BA|
	LDRH     r0, [r4, #0x12]
	CMP      r0, #0x40
	BNE      |loc_0802C3CE|
	LDR      r1, [r6]
	ADD      r0, r6, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802C3CE|
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [r0, #4]
	ADD      r4, r1, #0
	LDR      r1, [r1, #0x14]
	SUB      sp, #0x24
	CMP      r1, r0
	BNE      |sub_0802C3E6|
	MOV      r0, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|sub_0802C3E6|
|unk_0802C3E6|
; cited by 0x0802C344 (a pc-relative load targets 0x0802C3E8)
		LDR r7, [pc, #0x70]
		LDR r0, [r7]
		BL       |loc_080116FC|
		MOV r6, #1
		LSL r6, r6, #0xa
		CMP r0, r6
		BLT      |loc_0802C442|
		LSL r5, r6, #2
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r5, r0, r5
|loc_0802C400|
|unk_0802C400|
		ADD r0, sp, #0xc
		ADD r1, r4, #0
		BL       |loc_0800FE34|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r0, [sp, #8]
		MOV r2, #0x37
		STR r1, [sp, #0x1c]
		STR r0, [sp, #0x20]
		ADD r4, sp, #0x1c
		ADD r1, r4, #0
		STR r2, [sp, #8]
		MOV r3, #4
		MOV r0, #0
		LDR r2, [pc, #0x28]
		STR r5, [sp]
		STR r6, [sp, #4]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [r7]
		BL       |sub_0801191A|
|loc_0802C442|
		MOV r0, #1
		B        |inc_0x2bb4c_0x2d1c0| + 0x896
|sub_0802C446|
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802C456|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
|loc_0802C456|
	POP      {r3, pc}
	LDR      r1, [pc, #0xe0]
	LSR      r5, r6, #1
	BLS      |loc_0802C400|
	LSR      r7, r5, #1
	POP      {r3, r4, r7, pc}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x50]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x48]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_0802C482|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_0802C482|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x2c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x28]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0802C4AE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802C4AE|
	ADD      sp, #0x10
	POP      {r4, pc}
	LDR      r0, [pc, #0xc]
	SUB      r0, #4
	BX       lr
|sub_0802C4B8|
|unk_0802C4B8|
	INCBIN	baserom.gba_0x2c4b8_0x2c4ba.extracted
|sub_0802C4BA|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	ADD      r0, #0x8c
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x1b8]
	ADD      r4, r0, #0
	LDR      r1, [r6]
	ADD      r0, #0xc
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	SUB      sp, #0x14
	STMIA    r0!, {r2}
	LDR      r1, [r1]
	LDR      r5, [pc, #0x1a8]
	STR      r1, [r0]
	LDR      r1, [pc, #0x1a4]
	ADD      r5, #8
	LDR      r0, [r1]
	CMP      r0, #0
	BNE      |loc_0802C4FA|
	MOV      r0, #1
	STR      r0, [r1]
	LSL      r0, r0, #0xb
	SUB      r1, r5, #4
	STR      r0, [r1]
	LDR      r0, [pc, #0x194]
	STR      r0, [r5]
|loc_0802C4FA|
	MOV      r1, #0x14
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r0, [r6]
	MOV      r7, #0
	STRB     r7, [r0, #0x11]
	LDR      r1, [pc, #0x184]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [r6]
	LDR      r1, [sp, #0x18]
	LDR      r3, [pc, #0x174]
	ADD      r1, #0xff
	ADD      r1, #0xa1
	ADD      r3, #4
	LDR      r3, [r3]
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	ADD      r2, r2, r3
	LDR      r3, [r5]
	STR      r2, [sp, #4]
	ADD      r1, r1, r3
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	LDR      r2, [sp, #8]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	STMIA    r0!, {r1}
	LDR      r1, [sp, #0x10]
	STR      r1, [r0]
	LDR      r0, [r6]
	LDRB     r1, [r0, #8]
	ADD      r1, #0xff
	STRB     r1, [r0, #8]
	STR      r7, [r4, #8]
	STRB     r7, [r4, #0x15]
	MOV      r0, #0xff
	ADD      r0, #0x30
	STRB     r7, [r4, #0x14]
	BL       |inc_0x0158_0x143f2|
	ADD      r2, r0, #0
	LDR      r0, [pc, #0x13c]
	MOV      r1, #5
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	STR      r0, [r4, #4]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r7, r1, #0
	LDR      r1, [r0]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r6, r4, #0
	ADD      r6, #0xc
	ADD      r5, r6, #4
	CMP      r0, #0
	BEQ      |sub_0802C5BA|
	LDR      r1, [pc, #0x100]
	LDR      r2, [r6]
	LDR      r0, [r1]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STMIA    r0!, {r2}
	LDR      r2, [r5]
	STR      r2, [r0]
	LDR      r0, [r1]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r7]
	ADD      r0, r7, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	STRB     r0, [r4, #0x14]
	MOV      r0, #0x3c
	STRB     r0, [r4, #0x15]
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0802C5BA|
|unk_0802C5BA|
		MOV r1, #0x11
		LDR r0, [r4, #4]
		BL       |loc_0800EEB0|
		CMP r0, #0
		BNE      |loc_0802C62C|
		LDR r0, [pc, #0xcc]
		MOV r2, #0xf0
		LDR r1, [r0]
		LDRH r1, [r1, #4]
		AND r1, r2
		BEQ      |loc_0802C5DE|
		LDR r1, [pc, #0xb0]
		MOV r3, #1
		LDR r1, [r1]
		LDRB r2, [r1, #0x11]
		EOR r2, r3
		STRB r2, [r1, #0x11]
|loc_0802C5DE|
		MOV r3, #0x5a
		MOV r2, #0x14
		MOV r1, #0xf0
		LDR r0, [r0]
		BL       |inc_0x03d784_0x041118| + 0x2b00
		CMP r0, #0
		BEQ      |loc_0802C62C|
		LDR r0, [r4, #8]
		ADD r0, #1
		STR r0, [r4, #8]
		CMP r0, #5
		BNE      |loc_0802C62C|
		LDR r1, [pc, #0x88]
		LDR r2, [r6]
		LDR r0, [r1]
		ADD r0, #0xff
		ADD r0, #0xa1
		STMIA r0!, {r2}
		LDR r2, [r5]
		STR r2, [r0]
		LDR r0, [r1]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		LDR r1, [r7]
		ADD r0, r7, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #9
		BL       |loc_08046AA4|
		MOV r3, #1
		STRB r3, [r4, #0x14]
		MOV r0, #0x3c
		STRB r0, [r4, #0x15]
|loc_0802C62C|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xa6c
|sub_0802C630|
	LDRB     r1, [r0, #0x15]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	STRB     r2, [r0, #0x15]
	CMP      r1, #0
	BNE      |sub_0802C640|
	MOV      r0, #1
	BX       lr
|sub_0802C640|
|unk_0802C640|
		MOV r0, #0
		BX       lr
|sub_0802C644|
	LDR      r2, [r0, #4]
	CMP      r2, #0
	BNE      |loc_0802C64E|
	MOV      r0, #1
	BX       lr
|loc_0802C64E|
	LDRB     r2, [r0, #0x14]
	CMP      r2, #0
	BEQ      |sub_0802C668|
	CMP      r2, #1
	BNE      |loc_0802C66E|
	LDRB     r1, [r0, #0x15]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	STRB     r2, [r0, #0x15]
	CMP      r1, #0
	BNE      |loc_0802C66A|
	MOV      r0, #1
	BX       lr
|sub_0802C668|
|unk_0802C668|
		B        |inc_0x2bb4c_0x2d1c0| + 0xa18
|loc_0802C66A|
|unk_0802C66A|
		MOV r0, #0
		BX       lr
|loc_0802C66E|
|unk_0802C66E|
		MOV r0, #1
		BX       lr
|sub_0802C672|
	PUSH     {r3, lr}
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802C682|
	LDR      r1, [pc, #0x18]
	STR      r1, [r0]
|loc_0802C682|
	POP      {r3, pc}
|sub_0802C684|
|unk_0802C684|
	INCBIN	baserom.gba_0x2c684_0x2c686.extracted
|sub_0802C686|
	LSL      r0, r0, #0xc
	ADD      r0, #0x94
	LSL      r0, r0, #0xc
	BL       |loc_0802d674| + 0x1a
	SUB      r0, r0, r4
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #0x150]
	LSR      r5, r6, #1
|unk_0802C698|
	INCBIN	baserom.gba_0x2c698_0x2c69a.extracted
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	BNE      |sub_0802C6B0|
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802C6B0|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
|sub_0802C6B0|
|unk_0802C6B0|
		LDR r0, [pc, #0xcc]
		STR r0, [r4]
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r5, r0, #1
		MOV r0, #0xff
		ADD r0, #1
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r1, r0, #0
		ADD r1, #0x40
		LSL r1, r1, #0x18
		LDR r2, [pc, #0xb8]
		LSR r1, r1, #0x16
		LDR r1, [r2, r1]
		LSL r0, r0, #0x18
		MUL r1, r5
		ASR r1, r1, #0xa
		STR r1, [r4, #4]
		LSR r0, r0, #0x16
		LDR r0, [r2, r0]
		MUL r0, r5
		ASR r0, r0, #0xa
		STR r0, [r4, #8]
		MOV r0, #0
		STR r0, [r4, #0xc]
		STR r0, [r4, #0x10]
		ADD r0, r4, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xb62
|sub_0802C6EC|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0xc]
	SUB      sp, #0x34
	CMP      r0, #0
	BEQ      |sub_0802C6FE|
	MOV      r0, #1
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_0802C6FE|
|unk_0802C6FE|
		LDR r0, [pc, #0x88]
		LDR r5, [r0]
		CMP r5, #0
		BNE      |loc_0802C70A|
		MOV r0, #1
		B        |inc_0x2bb4c_0x2d1c0| + 0xbae
|loc_0802C70A|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r3, r4, #4
		LDR r6, [r4, #0x10]
		ADD r2, r3, #4
		ADD r0, #0xa1
		CMP r6, #0
		BEQ      |loc_0802C730|
		SUB r6, #1
		STR r6, [r4, #0x10]
		LDR r1, [r0]
		LDR r3, [r3]
		SUB r1, r1, r3
		STR r1, [r0]
		LDR r1, [r0, #4]
		LDR r2, [r2]
		SUB r1, r1, r2
		STR r1, [r0, #4]
		B        |loc_0802C776|
|loc_0802C730|
		LDR r6, [r0]
		LDR r3, [r3]
		MOV r7, #0x10
		ADD r3, r6, r3
		STR r3, [r0]
		LDR r3, [r0, #4]
		LDR r2, [r2]
		MOV r6, sp
		ADD r2, r3, r2
		STR r2, [r0, #4]
		STR r1, [sp, #0x20]
		LDRB r0, [r1, #0x10]
		ADD r3, sp, #0
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x3c]
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x1c]
		LSL r0, r7, #6
		STR r0, [sp, #0x18]
		MOV r0, #0
		STRB r0, [r3]
		ADD r0, r6, #4
		BL       |loc_0800FE78|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x24]
		ADD r3, r2, r1
		ADD r2, r6, #0
		MOV r1, #1
		BL       |inc_0x046118_0x049114| + 0x98e
		CMP r0, #0
		BEQ      |loc_0802C776|
		STR r7, [r4, #0x10]
|loc_0802C776|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xbae
	INCBIN  baserom.gba_0x2c77a_0x2c782.extracted
|sub_0802C782|
	LSR      r4, r0, #0x20
	LDR      r4, [r5, #0x6c]
	LSR      r3, r7, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0802C7AC|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802C7AC|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0802C7AC|
|unk_0802C7AC|
		ADD r2, r7, #0
		MOV r1, #0x40
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x144]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		MOV r0, #0
		STR r0, [r4, #0x48]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LDR r0, [pc, #0x134]
		LDR r2, [pc, #0x134]
		STR r0, [r4, #0x18]
		LSL r0, r6, #3
		LDR r1, [r2, r0]
		ADD r0, r0, r2
		STR r1, [r4, #0x40]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xc5e
|sub_0802C7EA|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x40
	ADD      r7, r1, #0
	LDR      r1, [r4, #0x20]
	LDMIA    r0!, {r2}
	SUB      sp, #0x34
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r0]
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x48]
	LDR      r1, [pc, #0xf8]
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1f
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r5, [pc, #0xe0]
	SUB      r5, #8
	LDR      r0, [r5, #4]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [r4, #0x30]
	CMP      r1, r2
	BGE      |loc_0802C85C|
	LDR      r1, [r4, #0x28]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_0802C85C|
	LDR      r1, [r0, #4]
	LDR      r2, [r4, #0x34]
	CMP      r1, r2
	BGE      |loc_0802C85C|
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BGE      |loc_0802C85C|
	ADD      r0, r4, #0
	ADD      r0, #0x28
	LDR      r1, [r5, #4]
	ADD      r6, r0, #0
	ADD      r1, #0x80
	LDR      r1, [r1, #0x2c]
	BL       |inc_0x0158_0x143f2| + 0x91cc
	CMP      r0, #0
	BNE      |sub_0802C868|
|loc_0802C85C|
	ADD      r1, r4, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_0802C868|
|unk_0802C868|
		CMP r7, #0
		BEQ      |inc_0x2bb4c_0x2d1c0| + 0xd18
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		BEQ      |inc_0x2bb4c_0x2d1c0| + 0xd18
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r7, sp
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x88]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		LDMIA r6!, {r1, r2, r3, r6}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r6}
		MOV r0, #0
		ADD r3, sp, #0
		STRB r0, [r3]
		STR r4, [sp, #0x30]
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r5]
		BL       |loc_08011C70|
		CMP r0, #0
		BEQ      |inc_0x2bb4c_0x2d1c0| + 0xd18
		ADD r1, r4, #0
		LDR r0, [r5]
		BL       |loc_08011944|
		B        |inc_0x2bb4c_0x2d1c0| + 0xd18
|sub_0802C8AE|
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_0802C8F4|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_0802C8BE|
	MOV      r0, #0
	POP      {r3, pc}
|sub_0802C8BE|
|unk_0802C8BE|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_0802C8F0|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0802C8F0|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_0802C8F0|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_0802C8F0|
		ADD r1, r0, #0
		LDR r0, [pc, #0x20]
		SUB r0, #8
		LDR r0, [r0]
		BL       |loc_08011944|
		MOV r0, #1
		B        |inc_0x2bb4c_0x2d1c0| + 0xd70
|loc_0802C8F0|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xd70
|loc_0802C8F4|
|unk_0802C8F4|
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		B        |inc_0x2bb4c_0x2d1c0| + 0xd70
	INCBIN  baserom.gba_0x2c8fa_0x2c8fe.extracted
|sub_0802C8FE|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0x70]
	LSR      r5, r6, #1
	LDR      r1, [pc, #0x1f0]
	LSR      r5, r6, #1
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	LSL      r3, r0, #4
	LDR      r1, [pc, #0x194]
	ADD      r0, r3, r0
	STRB     r0, [r1, #0xc]
	STRB     r0, [r1, #0xd]
	BX       lr
	LDR      r0, [pc, #0x18c]
	LDR      r2, [pc, #0x18c]
	LDRH     r1, [r0]
	MOV      r0, #0x40
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r0, r1
	STRH     r0, [r2]
	BX       lr
	LDR      r0, [pc, #0x168]
	LDR      r2, [pc, #0x164]
	LDRH     r1, [r0]
	MOV      r0, #0x40
	BIC      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	BIC      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	BIC      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	BIC      r1, r0
	STRH     r1, [r2]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0, #4]
	ADD      r1, #1
	STR      r1, [r0, #4]
	LDR      r0, [r0, #8]
	CMP      r1, r0
	BLT      |Mosaic_WriteSize1|
	MOV      r0, #1
	POP      {r3, pc}
|Mosaic_WriteSize1|
|unk_0802C976|
		LSL r1, r1, #4
		BL       |sub_08046E58|
		MOV r1, #0xf
		SUB r0, r1, r0
		LSL r3, r0, #4
		LDR r1, [pc, #0x120]
		ADD r0, r3, r0
		STRB r0, [r1, #0xc]
		STRB r0, [r1, #0xd]
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xe28
|sub_0802C98E|
	LDR      r1, [pc, #0x114]
	PUSH     {r3, lr}
	MOV      r0, #0xff
	STRB     r0, [r1, #0xc]
	STRB     r0, [r1, #0xd]
	MOV      r0, #0x37
	MVN      r0, r0
	LDRH     r0, [r0, r1]
	MOV      r1, #0x40
	ORR      r0, r1
	LDR      r1, [pc, #0x104]
	STRH     r0, [r1]
	LDRH     r0, [r1, #2]
	ADD      r2, r1, #2
	MOV      r1, #0x40
	ORR      r0, r1
	STRH     r0, [r2]
	ADD      r2, #2
	LDRH     r0, [r2]
	ORR      r0, r1
	STRH     r0, [r2]
	ADD      r2, #2
	LDRH     r0, [r2]
	ORR      r0, r1
	STRH     r0, [r2]
	LSL      r2, r1, #3
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0xe4]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0xdc]
	LDR      r0, [pc, #0xe0]
	BL       |inc_0x049120_0x055620| + 0x24
	POP      {r3, pc}
	LDR      r2, [pc, #0xc8]
	PUSH     {r3, lr}
	MOV      r1, #0
	STRB     r1, [r2, #0xc]
	STRB     r1, [r2, #0xd]
	MOV      r1, #0x37
	MVN      r1, r1
	LDRH     r2, [r1, r2]
	MOV      r1, #0x40
	LDR      r3, [pc, #0xb8]
	BIC      r2, r1
	STRH     r2, [r3]
	ADD      r3, #2
	LDRH     r2, [r3]
	BIC      r2, r1
	STRH     r2, [r3]
	ADD      r3, #2
	LDRH     r2, [r3]
	BIC      r2, r1
	STRH     r2, [r3]
	ADD      r3, #2
	LDRH     r2, [r3]
	BIC      r2, r1
	STRH     r2, [r3]
	CMP      r0, #0
	BEQ      |loc_0802CA1A|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802CA1A|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0, #4]
	ADD      r1, #1
	STR      r1, [r0, #4]
	LDR      r0, [r0, #8]
	CMP      r1, r0
	BLT      |Mosaic_WriteSize2|
	MOV      r0, #1
	POP      {r3, pc}
|Mosaic_WriteSize2|
|unk_0802CA2E|
		LSL r1, r1, #4
		BL       |sub_08046E58|
		LSL r3, r0, #4
		LDR r1, [pc, #0x6c]
		ADD r0, r3, r0
		STRB r0, [r1, #0xc]
		STRB r0, [r1, #0xd]
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xee0
|Bg_WriteControl0AndMosaic2|
	LDR      r1, [pc, #0x60]
	MOV      r0, #0
	STRB     r0, [r1, #0xc]
	STRB     r0, [r1, #0xd]
	MOV      r0, #0x37
	MVN      r0, r0
	LDRH     r1, [r0, r1]
	MOV      r0, #0x40
	LDR      r2, [pc, #0x54]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r0, r1
	STRH     r0, [r2]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	MOV      r1, #0
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	LDR      r0, [pc, #0x28]
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r0, r4, #0
	BEQ      |loc_0802CAA0|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802CAA0|
	POP      {r4, pc}
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	LSL      r0, r1, #0
	LSL      r0, r0, #0x10
	STR      r4, [r5, #0x30]
	LSR      r5, r0, #0x20
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
	PUSH     {r4, r5}
	LDR      r1, [r1, #4]
	LDR      r4, [r0, #8]
	LDR      r5, [r1, #0x24]
	SUB      sp, #8
	SUB      r4, r4, r5
	LDR      r5, [r0, #0xc]
	LDR      r3, [r1, #0x28]
	STR      r4, [sp]
	SUB      r3, r5, r3
	STR      r3, [sp, #4]
	ADD      r3, r4, #0
	ADD      r2, r1, #0
	ADD      r2, #0x2c
	LDR      r4, [sp, #4]
	LDR      r5, [r2]
	ADD      r3, r5, r3
	STR      r3, [r2]
	LDR      r3, [r2, #4]
	ADD      r3, r3, r4
	STR      r3, [r2, #4]
	LDR      r2, [r0, #8]
	LDR      r0, [r0, #0xc]
	STR      r0, [r1, #0x28]
	STR      r2, [r1, #0x24]
	LDR      r0, [r1, #0x30]
	LDR      r2, [r1, #0x18]
	ADD      r0, r0, r2
	STR      r0, [r1, #4]
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
|sub_0802CAF8|
|unk_0802CAF8|
		MOV r2, #0
|sub_0802CAFA|
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r5, r1, #0
	ADD      r0, #1
	LSL      r1, r0, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r5, #0x12]
	LDR      r0, [r4, #8]
	ADD      r6, r0, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	LDR      r1, [r4, #0x14]
	CMP      r1, r0
	BGT      |sub_0802CB4E|
	LDR      r0, [r4, #0xc]
	CMP      r0, #0
	BEQ      |loc_0802CB42|
	SUB      r0, #1
	STR      r0, [r4, #0xc]
	BNE      |loc_0802CB42|
	LDR      r0, [r4, #4]
	CMP      r0, #0
	BEQ      |loc_0802CB3A|
	ADD      r1, r0, #0
	MOV      r0, #1
	STR      r0, [r1, #0x14]
|loc_0802CB3A|
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xed20
	POP      {r4, r5, r6, pc}
|loc_0802CB42|
	LDR      r0, [r4, #0x10]
	MUL      r0, r6
	STRH     r0, [r5, #0x12]
	LDR      r0, [r4, #0x10]
	STRB     r0, [r5, #0x11]
	POP      {r4, r5, r6, pc}
|sub_0802CB4E|
|unk_0802CB4E|
		STRB r0, [r5, #0x11]
		POP {r4, r5, r6, pc}
|sub_0802CB52|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [r1, #4]
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	MOV      r1, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |loc_0802CB64|
	ADD      r1, r4, #0
|loc_0802CB64|
	STR      r1, [sp]
	LDR      r1, [r4, #0xc]
	MOV      r0, #0x18
	STR      r1, [sp, #4]
	LDR      r1, [r4, #0x10]
	STR      r1, [sp, #8]
	LDR      r6, [r4, #0x18]
	LDR      r7, [r4, #0x1c]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802CB90|
	LDR      r1, [pc, #0x2c]
	STR      r1, [r0]
	LDR      r1, [sp]
	STR      r1, [r0, #4]
	LDR      r1, [sp, #4]
	STR      r1, [r0, #8]
	LDR      r1, [sp, #8]
	ADD      r0, #0xc
	STMIA    r0!, {r1, r6, r7}
	SUB      r0, #0x18
|loc_0802CB90|
	ADD      r6, r0, #0
	LDRB     r0, [r4, #8]
	LDR      r1, [pc, #0x18]
	LDRB     r1, [r1, r0]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_0802CBAA|
|unk_0802CBAA|
	INCBIN	baserom.gba_0x2cbaa_0x2cbae.extracted
|sub_0802CBAE|
	LSR      r4, r0, #0x20
	MOV      r6, #0x70
	LSR      r7, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r1, #4]
	ADD      r1, r0, #0
	ADD      r1, #8
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb58
	ADD      r5, #0x10
	ADD      r4, #0xff
	ADD      r4, #1
	ADD      r4, #0x78
	LDMIA    r5!, {r0, r1}
	STMIA    r4!, {r0, r1}
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x24
	ADD      r4, r1, #0
	LDR      r1, [pc, #0x134]
	MOV      r2, #0x20
	MOV      r6, sp
	MOV      r0, sp
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0xff
	ADD      r0, #0xa1
	LDR      r0, [r0, r4]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0xc]
	MOV      r0, #0xff
	ADD      r0, #0xa5
	LDR      r0, [r0, r4]
	MOV      r1, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0xe]
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	STR      r0, [sp, #0x20]
	STR      r1, [r0, #0x34]
	LDRH     r0, [r3, #0xe]
	LDR      r1, [pc, #0x10c]
	ADD      r7, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	LDR      r0, [pc, #0x100]
	MOV      r3, #0
	ADD      r4, r0, r1
	ADD      r2, r4, #0
	ADD      r1, r6, #0
	MVN      r3, r3
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r5, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xe4]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r0, [sp, #0x20]
	ADD      r3, sp, #0
	STR      r5, [r0, #0x30]
	MOV      r0, #0xff
	ADD      r0, #0xf5
	STR      r7, [r0, r5]
	LDRH     r0, [r3, #0xe]
	ADD      r2, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r7, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xb8]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0xff
	ADD      r0, #0xf1
	STR      r7, [r0, r5]
	ADD      r1, r0, #4
	STR      r5, [r1, r7]
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0xe]
	ADD      r2, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r5, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x88]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0xff
	ADD      r0, #0xf1
	STR      r5, [r0, r7]
	ADD      r1, r0, #4
	STR      r7, [r1, r5]
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0xe]
	ADD      r2, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r7, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x5c]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0xff
	ADD      r0, #0xf1
	STR      r7, [r0, r5]
	ADD      r1, r0, #4
	STR      r5, [r1, r7]
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0xe]
	ADD      r2, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x2c]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #0xff
	ADD      r1, #0xf1
	STR      r4, [r1, r7]
	ADD      r4, #0xff
	ADD      r4, #0xc1
	MOV      r0, #0
	ADD      r4, #0x30
	STMIA    r4!, {r0, r7}
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802CD0E|
	LDR      r1, [pc, #0x10]
	STR      r1, [r0]
|loc_0802CD0E|
	POP      {r3, pc}
|sub_0802CD10|
|unk_0802CD10|
	INCBIN	baserom.gba_0x2cd10_0x2cd12.extracted
|sub_0802CD12|
	LSR      r5, r6, #1
	LSR      r4, r4, #0x1e
	LSL      r0, r0, #0
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	STMIA    r2!, {r2, r3, r4}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	BEQ      |loc_0802CD40|
	MOV      r0, #0xb0
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	CMP      r5, r0
	BNE      |sub_0802CD42|
	MOV      r0, #0xaf
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
|loc_0802CD40|
	POP      {r3, r4, r5, pc}
|sub_0802CD42|
|unk_0802CD42|
		MOV r0, #0xff
		ADD r0, #2
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0802CD60|
		MOV r0, #0xb2
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_0802CD40|
|loc_0802CD60|
		MOV r0, #0x56
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0802CD40|
		MOV r0, #0xac
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x2cd76_0x2cd78.extracted
|sub_0802CD78|
|unk_0802CD78|
	INCBIN	baserom.gba_0x2cd78_0x2cd7c.extracted
	LDR      r0, [pc, #0]
	BX       lr
|sub_0802CD80|
|unk_0802CD80|
	INCBIN	baserom.gba_0x2cd80_0x2cd82.extracted
|sub_0802CD82|
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	BEQ      |loc_0802CDA4|
	MOV      r0, #0xaf
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	CMP      r5, r0
	BNE      |sub_0802CDA6|
	MOV      r0, #0xb0
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
|loc_0802CDA4|
	POP      {r3, r4, r5, pc}
|sub_0802CDA6|
|unk_0802CDA6|
		MOV r0, #0xb2
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0802CDC4|
		MOV r0, #0xff
		ADD r0, #2
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_0802CDA4|
|loc_0802CDC4|
		MOV r0, #0xac
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0802CDA4|
		MOV r0, #0x56
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_0802CDA4|
	INCBIN  baserom.gba_0x2cde0_0x2cde4.extracted
|sub_0802CDE4|
	ADD      r0, #0xa4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r1, #0x11]
	ADD      r6, r1, #0
	SUB      sp, #0x44
	CMP      r0, #1
	BEQ      |loc_0802CDFA|
	CMP      r0, #4
	BNE      |sub_0802CE00|
|loc_0802CDFA|
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|sub_0802CE00|
|unk_0802CE00|
		LDR r0, [pc, #0x288]
		LDR r1, [r0]
		CMP r1, #0
		BNE      |loc_0802CE0C|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x12b0
|loc_0802CE0C|
		ADD r0, sp, #8
		BL       |sub_0800FDFA|
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x10]
		LDR r2, [sp, #0x14]
		ADD r1, r0, r1
		LDR r0, [sp, #0xc]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp]
		STR r1, [sp, #0x18]
		STR r0, [sp, #4]
		STR r0, [sp, #0x1c]
		MOV r5, #1
		ADD r1, r6, #0
		ADD r0, sp, #0x20
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x20]
		LDR r1, [sp, #0x28]
		LDR r2, [sp, #0x2c]
		ADD r1, r0, r1
		LDR r0, [sp, #0x24]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0x34]
		ASR r1, r1, #1
		LDR r0, [sp, #0x18]
		STR r1, [sp]
		SUB r0, r0, r1
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x34]
		STR r0, [sp]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		STR r0, [sp, #0x38]
		BGE      |loc_0802CE6E|
		NEG r0, r2
|loc_0802CE6E|
		ADD r1, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGE      |loc_0802CE78|
		NEG r0, r0
|loc_0802CE78|
		ADD r7, r1, #0
		CMP r1, r0
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x34]
		BLE      |loc_0802CE90|
		LDR r1, [sp, #0x38]
		MOV r0, #3
		CMP r1, #0
		BGT      |loc_0802CE8C|
		MOV r0, #2
|loc_0802CE8C|
		STRB r0, [r6, #0x10]
		B        |loc_0802CE9C|
|loc_0802CE90|
		ADD r7, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BLE      |loc_0802CE9A|
		MOV r5, #0
|loc_0802CE9A|
		STRB r5, [r6, #0x10]
|loc_0802CE9C|
		CMP r7, #8
		BGE      |loc_0802CEA4|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x12b0
|loc_0802CEA4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_0802CEC4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_0802CEC4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		LDR r0, [sp, #0x38]
		LDR r1, [sp, #0x3c]
		LSL r0, r0, #8
		LSL r1, r1, #8
		STR r1, [sp, #0x34]
		STR r0, [sp, #0x30]
		LDR r1, [r4, #4]
		LDR r2, [sp, #0x34]
		MUL r0, r1
		MUL r2, r1
		ASR r1, r2, #8
		ASR r0, r0, #8
		ADD r5, r6, #0
		ADD r5, #0xff
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x14]
		LSL r1, r0, #8
		ADD r5, #0xa1
		STR r0, [sp, #8]
		STR r0, [sp, #0x10]
		LSL r7, r7, #8
		ADD r0, r7, #0
		BL       |sub_08046E58|
		STR r0, [sp, #4]
		LDR r0, [sp, #0x14]
		LSL r1, r0, #8
		ADD r0, r7, #0
		BL       |sub_08046E58|
		LDR r1, [sp, #4]
		STR r0, [sp, #0xc]
		ADD r0, r1, #0
		STR r1, [sp, #8]
		LDR r1, [sp, #0xc]
		STR r0, [sp, #0x18]
		STR r1, [sp, #0x1c]
		LDR r0, [r5]
		LDR r1, [sp, #0x18]
		ADD r7, r5, #4
		ADD r0, r0, r1
		LDR r1, [r5, #4]
		LDR r2, [sp, #0x1c]
		STR r0, [sp, #8]
		ADD r1, r1, r2
		STR r0, [sp, #0x28]
		STR r0, [sp, #0x20]
		MOV r0, #0
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x24]
		STR r0, [sp, #0x24]
		STR r1, [sp, #0x2c]
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_0802CFE0|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x28
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0802CF60|
		LDR r0, [sp, #0x28]
		STR r0, [r5]
		LDR r0, [sp, #0x2c]
		STR r0, [r7]
		MOV r0, #1
		STR r0, [sp, #0x24]
		B        |loc_0802CFE0|
|loc_0802CF60|
		LDR r0, [sp, #0x28]
		STR r0, [sp, #0x1c]
		ADD r0, r6, #0
		ADD r0, #0xff
		ADD r0, #0xa5
		STR r0, [sp, #0x40]
		LDR r0, [r0]
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x28]
		LDR r1, [r5]
		SUB r0, r0, r1
		STR r0, [sp, #0x18]
		BPL      |loc_0802CF7C|
		NEG r0, r0
|loc_0802CF7C|
		MOV r1, #1
		LSL r1, r1, #0xa
		CMP r0, r1
		BLE      |loc_0802CFA4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x1c
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0802CFA4|
		LDR r0, [sp, #0x1c]
		STR r0, [r5]
		LDR r0, [sp, #0x20]
		STR r0, [r7]
		MOV r0, #1
		STR r0, [sp, #0x24]
		B        |loc_0802CFE0|
|loc_0802CFA4|
		LDR r0, [r5]
		LDR r2, [sp, #0x2c]
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x2c]
		ADD r1, sp, #0x1c
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x40]
		LDR r0, [r0]
		SUB r0, r2, r0
		STR r0, [sp, #0x18]
		BPL      |loc_0802CFBC|
		NEG r0, r0
|loc_0802CFBC|
		MOV r2, #1
		LSL r2, r2, #0xa
		CMP r0, r2
		BLE      |loc_0802CFE0|
		LDR r2, [r6]
		ADD r0, r6, #0
		LDR r3, [r2, #0x54]
		ADD r2, r3, r2
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0802CFE0|
		LDR r0, [sp, #0x1c]
		STR r0, [r5]
		LDR r0, [sp, #0x20]
		STR r0, [r7]
		MOV r0, #1
		STR r0, [sp, #0x24]
|loc_0802CFE0|
		LDR r0, [sp, #0x24]
		CMP r0, #0
		BNE      |loc_0802D074|
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_0802CFF6|
		MOV r0, #0x20
		BL       |inc_0x03d784_0x041118| + 0x2348
		SUB r0, #0x10
		STR r0, [r4, #8]
|loc_0802CFF6|
		LDR r0, [r5, #4]
		LDR r1, [r5]
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x38]
		STR r1, [sp, #0x1c]
		CMP r0, #0
		BGE      |loc_0802D006|
		NEG r0, r0
|loc_0802D006|
		LDR r2, [sp, #0x3c]
		CMP r2, #0
		BGE      |loc_0802D00E|
		NEG r2, r2
|loc_0802D00E|
		CMP r0, r2
		LDR r0, [r4, #8]
		ADD r1, sp, #0x1c
		BGE      |loc_0802D03A|
		CMP r0, #0
		BGE      |loc_0802D02A|
		LDR r0, [sp, #0x1c]
		LDR r2, [r4, #4]
		SUB r0, r0, r2
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #8]
		ADD r0, #1
		STR r0, [r4, #8]
		B        |loc_0802D05C|
|loc_0802D02A|
		LDR r0, [sp, #0x1c]
		LDR r2, [r4, #4]
		ADD r0, r0, r2
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #8]
		SUB r0, #1
		STR r0, [r4, #8]
		B        |loc_0802D05C|
|loc_0802D03A|
		CMP r0, #0
		BGE      |loc_0802D04E|
		LDR r0, [sp, #0x20]
		LDR r2, [r4, #4]
		SUB r0, r0, r2
		STR r0, [sp, #0x20]
		LDR r0, [r4, #8]
		ADD r0, #1
		STR r0, [r4, #8]
		B        |loc_0802D05C|
|loc_0802D04E|
		LDR r0, [sp, #0x20]
		LDR r2, [r4, #4]
		ADD r0, r0, r2
		STR r0, [sp, #0x20]
		LDR r0, [r4, #8]
		SUB r0, #1
		STR r0, [r4, #8]
|loc_0802D05C|
		LDR r2, [r6]
		ADD r0, r6, #0
		LDR r3, [r2, #0x54]
		ADD r2, r3, r2
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0802D076|
		LDR r0, [sp, #0x1c]
		STR r0, [r5]
		LDR r0, [sp, #0x20]
		STR r0, [r7]
|loc_0802D074|
		B        |loc_0802D07A|
|loc_0802D076|
		MOV r0, #0
		STR r0, [r4, #8]
|loc_0802D07A|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x12b0
|sub_0802D08C|
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802D0A8|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	MOV      r1, #0
	STR      r1, [r0, #8]
|loc_0802D0A8|
	POP      {r4, pc}
	LSL      r0, r0, #0
	STMIA    r6!, {r4, r5, r6}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0
	STRH     r1, [r4, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r4, #8]
	STRB     r1, [r4, #0x11]
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r0, [pc, #0x10c]
	MOV      r2, #0
	MOV      r1, #0x24
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11b72
	CMP      r0, #0xc
	BLT      |loc_0802D0DA|
	MOV      r0, #0x18
	STRH     r0, [r4, #0x12]
|loc_0802D0DA|
	POP      {r4, pc}
	PUSH     {r4, r5, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x18
	BCC      |sub_0802D102|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
|sub_0802D102|
|unk_0802D102|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #8
		BNE      |inc_0x2bb4c_0x2d1c0| + 0x15b2
		LDR r5, [pc, #0xc4]
		LDR r0, [r5]
		BL       |loc_080116FC|
		CMP r0, #0x80
		BLT      |inc_0x2bb4c_0x2d1c0| + 0x15b2
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDRB r0, [r4, #0x10]
		ADD r1, r5, #4
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		MOV r2, #0
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		STR r2, [sp]
		ADD r3, r4, #0
		MOV r0, #0
		LDRB r2, [r4, #0x10]
		ADD r1, sp, #0x14
		BL       |sub_0802d79c|
		ADD r1, r0, #0
		LDR r0, [r5]
	INCBIN  baserom.gba_0x2d166_0x2d168.extracted
|sub_0802D168|
|unk_0802D168|
	INCBIN	baserom.gba_0x2d168_0x2d16c.extracted
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x68]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x60]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_0802D18A|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_0802D18A|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x44]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x40]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0802D1B6|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802D1B6|
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_0802D1BA|
|unk_0802D1BA|
		MOV r2, #1
		LDR r1, [r1, #0x14]
		LDR r3, [pc, #0x20]