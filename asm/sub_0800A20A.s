	CODE16
|sub_0800A20A|
	LSR      r4, r0, #0x20
|unk_0800A20C|
	INCBIN	baserom.gba_0xa20c_0xa20e.extracted
	LSR      r4, r0, #0x20
|loc_0800A210|
|unk_0800A210|
	INCBIN	baserom.gba_0xa210_0xa212.extracted
	LSR      r4, r0, #0x20
|unk_0800A214|
	INCBIN	baserom.gba_0xa214_0xa216.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [r0, #4]
	SUB      r1, #1
	STR      r1, [r0, #4]
	LSR      r0, r1, #0x1f
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0800A248|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800A248|
	LDRB     r0, [r5, #6]
	MOV      r3, #4
	STRB     r0, [r4, #0x10]
	LDRSH    r4, [r5, r3]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800A260|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0800A260|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	BMI      |loc_0800A210|
	LSR      r4, r0, #0x20
	BX       lr
|sub_0800A26A|
|unk_0800A26A|
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0xa26e_0xa272.extracted
