	CODE16
|sub_0800A8D8|
	MOV      r2, #1
	STRB     r2, [r1, #0x10]
	LDR      r1, [r0, #4]
	SUB      r1, #1
	STR      r1, [r0, #4]
	POP      {r4, r5}
	LSR      r0, r1, #0x1f
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r4, [r4, #4]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800A90C|
	LDR      r1, [pc, #0x30]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0800A90C|
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r4, [r4, #4]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800A932|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0800A932|
	POP      {r4, pc}
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
|unk_0800A938|
	INCBIN	baserom.gba_0xa938_0xa93a.extracted
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_0800A94E|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800A958|
|loc_0800A94E|
	MOV      r1, #0xff
	STRB     r1, [r0, #4]
	MOV      r1, #0
	STR      r1, [r0]
	STR      r4, [r0, #8]
|loc_0800A958|
	POP      {r4, pc}
