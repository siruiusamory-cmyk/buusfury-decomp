	CODE16
|sub_0800A134|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800A148|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800A148|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |sub_08009D24|
	LDR      r0, [pc, #0xb4]
	STR      r0, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800A17C|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800A17C|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |sub_08009D24|
	LDR      r0, [pc, #0x80]
	STR      r0, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x70]
	STR      r0, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0xf
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	ADD      r6, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800A1C2|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800A1C2|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_08009D24|
	LDR      r0, [pc, #0x40]
	STR      r0, [r4]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800A1E8|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800A1E8|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |sub_08009D24|
	LDR      r0, [pc, #0x20]
	STR      r0, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|sub_0800A208|
|unk_0800A208|
	INCBIN	baserom.gba_0xa208_0xa20a.extracted
	CODE16
|dat_0800A20A|
	DCW      0x0804
|unk_0800A20C|
	INCBIN	baserom.gba_0xa20c_0xa20e.extracted
|dat_0800A20E|
	DCW      0x0804
|loc_0800A210|
|unk_0800A210|
	INCBIN	baserom.gba_0xa210_0xa212.extracted
|dat_0800A212|
	DCW      0x0804
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
|sub_0800A272|
	DCW      0x0000
	DCW      0x1af0
	DCW      0x0300

