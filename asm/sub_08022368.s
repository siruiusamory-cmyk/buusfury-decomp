	CODE16
|sub_08022368|
	LDR      r1, [pc, #0x2b0]
	STR      r1, [r0, #0x34]
	BX       lr
	LDR      r1, [pc, #0x290]
	SUB      r1, #2
	STR      r1, [r0, #0x34]
	BX       lr
	LDR      r1, [pc, #0x2a8]
	STR      r1, [r0, #0x34]
	BX       lr
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x38]
	ADD      r1, #1
	STR      r1, [r0, #0x38]
	LSL      r1, r1, #0x1c
	LSR      r2, r1, #0x1e
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r1, [r0, #0x34]
	LSL      r2, r2, #2
	ADD      r1, r1, r2
	LDR      r2, [r0, #0x28]
	CMP      r2, r1
	BEQ      |loc_080223B0|
	STR      r1, [r0, #0x28]
	LDRB     r3, [r1, #2]
|loc_0802239C|
	LDRB     r4, [r1, #3]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0x268]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080223B0|
	POP      {r4, pc}
	LDR      r2, [pc, #0x254]
	PUSH     {r4, r5, r6}
	LDR      r2, [r2, #8]
	LDR      r4, [r0, #0x2c]
	ADD      r2, #0x18
	LDR      r5, [r2]
	SUB      sp, #8
	SUB      r4, r4, r5
	LDR      r5, [r0, #0x30]
	LDR      r2, [r2, #4]
	STR      r4, [sp]
	SUB      r2, r5, r2
	STR      r2, [sp, #4]
	ADD      r2, r4, #0
	ADD      r3, r0, #0
	ADD      r3, #0x20
	LDR      r4, [sp, #4]
	STMIA    r3!, {r2, r4}
	LDR      r4, [r0, #0x28]
	MOV      r3, #0
	LDRSB    r5, [r4, r3]
	LDR      r2, [r0, #0x20]
	MOV      r3, #1
	SUB      r2, r2, r5
	STR      r2, [r0, #0x20]
	LDRSB    r5, [r4, r3]
	LDR      r2, [r0, #0x24]
	MOV      r6, #3
	SUB      r2, r2, r5
	STR      r2, [r0, #0x24]
	LDR      r2, [r1]
	LDR      r4, [r4, #4]
	LDR      r5, [pc, #0x230]
	STR      r4, [r2]
	LDR      r3, [r0, #0x20]
	AND      r4, r5
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r3, r4
	STR      r3, [r2]
	LDR      r4, [r0, #0x24]
	LSR      r3, r3, #8
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	LSL      r3, r3, #8
	ORR      r3, r4
	STR      r3, [r2]
	LDRH     r3, [r0, #0xc]
	LDR      r4, [r2, #4]
	LSL      r6, r6, #0xa
	LSR      r4, r4, #0xa
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	LSL      r4, r4, #0xa
	ORR      r3, r4
	BIC      r3, r6
	STR      r3, [r2, #4]
	LDR      r3, [r0, #0x28]
	MOV      r4, #1
	LDR      r3, [r3, #4]
	LSL      r4, r4, #0x1d
	ORR      r3, r4
	ADD      r2, #8
	STR      r3, [r2]
	LDR      r4, [r0, #0x20]
	AND      r3, r5
	LSL      r4, r4, #0x17
	LSR      r4, r4, #7
	ORR      r3, r4
	STR      r3, [r2]
	LDR      r5, [r0, #0x28]
	LDR      r4, [r0, #0x24]
	LDRB     r5, [r5, #3]
	LSR      r3, r3, #8
	LSL      r3, r3, #8
	ADD      r4, r4, r5
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	ORR      r3, r4
	STR      r3, [r2]
	LDRH     r0, [r0, #0xc]
	LDR      r3, [r2, #4]
	LSR      r3, r3, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r3, r3, #0xa
	ORR      r0, r3
	BIC      r0, r6
	STR      r0, [r2, #4]
	ADD      r2, #8
	STR      r2, [r1]
	ADD      sp, #8
	POP      {r4, r5, r6}
	MOV      r0, #0
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_08022488|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08022488|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08022488|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_080222E0|
	LDR      r0, [pc, #0x194]
	MOV      r1, #0
	STR      r0, [r4]
	LDR      r2, [r5]
	LDR      r5, [r5, #4]
	LSL      r2, r2, #8
	STR      r1, [r4, #0x44]
	LSL      r5, r5, #8
	STR      r2, [r4, #0x3c]
	ADD      r0, r4, #0
	ADD      r0, #0x44
	STR      r5, [r4, #0x40]
	STR      r1, [r4, #0x48]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x38]
	SUB      sp, #0x1c
	ADD      r0, #1
	STR      r0, [r4, #0x38]
	LSL      r0, r0, #0x1c
	LSR      r1, r0, #0x1e
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r0, [r4, #0x34]
	LSL      r1, r1, #2
	ADD      r1, r0, r1
	LDR      r0, [r4, #0x28]
	CMP      r0, r1
	BEQ      |loc_080224E4|
	STR      r1, [r4, #0x28]
	LDRB     r2, [r1, #2]
	LDRB     r0, [r1, #3]
	LDR      r3, [pc, #0x138]
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r1, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080224E4|
	LDR      r0, [r4, #0x44]
	LDR      r1, [r4, #0x48]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	ADD      r5, r4, #0
	ADD      r5, #0x44
	ADD      r6, r5, #4
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #8
	LSL      r0, r0, #8
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x10]
	LSL      r1, r0, #8
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	MOV      r0, #1
	LSL      r0, r0, #0xa
	BL       |inc_0x046118_0x049114| + 0xd40
	ADD      r7, r0, #0
	LDR      r0, [sp, #0x10]
	LSL      r1, r0, #8
	MOV      r0, #1
	LSL      r0, r0, #0xa
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp, #8]
	LDR      r1, [sp, #8]
	STR      r7, [sp, #4]
	STR      r7, [sp, #0x14]
	STR      r1, [sp, #0x18]
	STR      r7, [r5]
	LDR      r0, [sp, #0x18]
	LDR      r1, [pc, #0xd8]
	STR      r0, [r6]
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_08022542|
	LDR      r0, [r4, #0x44]
	SUB      r0, #0xff
	SUB      r0, #1
	STR      r0, [r4, #0x44]
|loc_08022542|
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_08022554|
	LDR      r0, [r4, #0x44]
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r0, [r4, #0x44]
|loc_08022554|
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x1f
	BEQ      |loc_08022566|
	LDR      r0, [r4, #0x48]
	SUB      r0, #0xff
	SUB      r0, #1
	STR      r0, [r4, #0x48]
|loc_08022566|
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_08022578|
	LDR      r0, [r4, #0x48]
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r0, [r4, #0x48]
|loc_08022578|
	LDR      r0, [r1, #8]
	LDR      r7, [r5]
	ADD      r3, r0, #0
	ADD      r3, #0x18
	ADD      r3, r3, #4
	LDMIA    r3!, {r1, r2, r3}
	LDR      r0, [r0, #0x18]
	MOV      ip, r3
	LDR      r3, [r4, #0x3c]
	ADD      r3, r3, r7
	STR      r3, [r4, #0x3c]
	LDR      r3, [r4, #0x40]
	LDR      r6, [r6]
	ADD      r3, r3, r6
	STR      r3, [r4, #0x40]
	ADD      r3, r4, #0
	ADD      r3, #0x2c
	STR      r3, [sp, #0x18]
	LDR      r6, [r4, #0x3c]
	ADD      r3, #0x10
	MOV      lr, r3
	LDR      r3, [r4, #0x40]
	ASR      r6, r6, #8
	ASR      r3, r3, #8
	STR      r3, [sp, #0x14]
	LDR      r3, [sp, #0x18]
	LDR      r7, [sp, #0x14]
	STR      r6, [sp, #0x10]
	STMIA    r3!, {r6, r7}
	LDR      r6, [r4, #0x2c]
	MOV      r3, #0
	CMP      r6, r0
	BGE      |loc_080225C4|
	STR      r0, [r4, #0x2c]
	LSL      r0, r0, #8
	MOV      r6, lr
	STR      r0, [r6]
	STR      r3, [r5]
|loc_080225C4|
	LDR      r0, [r4, #0x2c]
	CMP      r0, r2
	BLE      |loc_080225D4|
	MOV      r6, lr
	LSL      r0, r2, #8
	STR      r2, [r4, #0x2c]
	STR      r0, [r6]
	STR      r3, [r5]
|loc_080225D4|
	ADD      r0, r4, #0
	ADD      r2, r4, #0
	LDR      r5, [r4, #0x30]
	ADD      r2, #0x40
	ADD      r0, #0x48
	CMP      r5, r1
	BGE      |loc_080225EA|
	STR      r1, [r4, #0x30]
	LSL      r1, r1, #8
	STR      r1, [r2]
	STR      r3, [r0]
|loc_080225EA|
	LDR      r1, [r4, #0x30]
	CMP      r1, ip
	BLE      |loc_080225FA|
	MOV      r5, ip
	LSL      r1, r5, #8
	STR      r5, [r4, #0x30]
	STR      r1, [r2]
	STR      r3, [r0]
|loc_080225FA|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_080225FE|
	DCW      0x0000
	DCW      0xbf06,0x0872,0x9680,0x0804,0xbf94,0x0872,0xba50,0x0804
	DCW      0x0000,0x0601,0xca80,0x0804,0xe120,0x0804,0xbf34,0x0872
	DCW      0xbf64,0x0872,0xffff
|sub_08022626|
|unk_08022626|
	INCBIN	baserom.gba_0x22626_0x2262a.extracted
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	LDR      r1, [r2]
	ADD      r0, r2, #0
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	LSR      r0, r0, #0x1f
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x2c]
	ADD      r4, r1, #0
	LDR      r6, [r7]
	ADD      r1, r2, #0
	LDR      r2, [r4]
	ADD      r6, #0xc0
	LDR      r5, [r6, #8]
	LDR      r3, [r2, #4]
	ADD      r0, r4, #0
	ADD      r3, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r0, [r6, #8]
	CMP      r0, r5
	BNE      |loc_0802266C|
	ADD      r1, r4, #0
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x12532
|loc_0802266C|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0802266E|
|unk_0802266E|
	INCBIN	baserom.gba_0x2266e_0x22672.extracted
