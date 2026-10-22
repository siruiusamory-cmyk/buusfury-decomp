	CODE16
|sub_08033862|
	LSL      r0, r0, #0x18
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	LSL      r4, r2, #0
	LSL      r0, r0, #0x10
	MOV      r0, #0x43
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	STR      r4, [sp, #0x1c0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSL      r1, r5, #0x16
	LSL      r0, r0, #0
	LSL      r0, r2, #1
	LSL      r0, r0, #0x10
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	LDR      r1, [pc, #0x68]
	LDR      r4, [r1]
	LDR      r5, [r0, #4]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080338AC|
	MOV      r1, #1
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x58]
	STR      r1, [r0]
	STR      r5, [r0, #8]
	STR      r6, [r0, #0xc]
|loc_080338AC|
	ADD      r2, r0, #0
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r0, r4, r0
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080338D8|
	LDR      r1, [pc, #0x30]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080338D8|
	POP      {r4, pc}
	MOV      r2, #0x85
	LSL      r2, r2, #2
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	ADD      r1, r1, r2
	BL       |inc_0x0158_0x143f2| + 0x12430
	MOV      r0, #1
	POP      {r3, pc}
	MOV      r2, #0x85
	LSL      r2, r2, #2
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	ADD      r1, r1, r2
	BL       |inc_0x0158_0x143f2| + 0x12430
	POP      {r3, pc}
|sub_080338FC|
|unk_080338FC|
; cited by 0x08033890 (a pc-relative load targets 0x080338FC)
	INCBIN  baserom.gba_0x338fc_0x33908.extracted
		PUSH {r3, r4, r5, lr}
		ADD r4, r1, #0
		MOV r0, #0xff
		ADD r0, #0x15
		LDR r5, [r1, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0803392C|
		MOV r0, #0xff
		ADD r0, #0x13
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_08033966|
|loc_0803392C|
		MOV r0, #0xcb
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |sub_08033948|
		MOV r0, #0xca
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_08033966|
