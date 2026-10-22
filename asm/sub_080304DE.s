	CODE16
|sub_080304DE|
	LSR      r5, r6, #1
	ASR      r4, r7, #0xf
	LSR      r1, r6, #1
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	MOV      r5, #0
	STRH     r5, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	MOV      r0, #0xff
	ADD      r0, #0x77
	STRB     r5, [r1, #0x11]
	STRH     r5, [r0, r1]
	ADD      r0, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [pc, #0xf8]
	ADD      r0, r4, #0
	LDR      r1, [r1]
	ADD      r0, #0xff
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	ADD      r0, #0xa1
	STMIA    r0!, {r2}
	LDR      r1, [r1]
	STR      r1, [r0]
	LDR      r1, [r0]
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r1, [r0]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	STRB     r5, [r6, #4]
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r0, [pc, #0xcc]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	MOV      r2, #0xf0
	LDRH     r1, [r1, #4]
	AND      r1, r2
	BEQ      |loc_0803054E|
	LDRH     r1, [r4, #0x12]
	ADD      r1, #2
	STRH     r1, [r4, #0x12]
|loc_0803054E|
	MOV      r3, #0x5a
	MOV      r2, #0x10
	MOV      r1, #0xf3
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x2b00
	CMP      r0, #0
	BEQ      |loc_08030582|
	LDR      r0, [pc, #0xa4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	STRB     r0, [r4, #0x11]
	STRH     r0, [r4, #0x12]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08030582|
	POP      {r4, pc}
	LDRH     r0, [r1, #0x12]
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #7
	BLS      |loc_080305A8|
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	LDRB     r0, [r1, #0x11]
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r1, #0x11]
	CMP      r0, #5
	BLS      |loc_080305A8|
	MOV      r0, #4
	STRB     r0, [r1, #0x11]
|loc_080305A8|
	BX       lr
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x54]
	ADD      r5, r1, #0
	LDR      r4, [r6]
	MOV      r0, #0
	STRB     r0, [r4, #0x11]
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x4c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r1, [pc, #0x48]
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x10a60
	MOV      r1, #0x12
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x38]
	ADD      r1, #8
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x1c]
	LDR      r0, [r4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [pc, #0x1c]
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x10a60
	POP      {r4, pc}
	LDR      r0, [pc, #0x10]
	ADD      r0, #4
	BX       lr
|sub_08030604|
|unk_08030604|
	INCBIN	baserom.gba_0x30604_0x30606.extracted
