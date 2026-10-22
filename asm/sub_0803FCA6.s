	CODE16
|sub_0803FCA6|
	LSL      r0, r0, #0xc
	STRB     r4, [r5, #0x1b]
	LSR      r3, r7, #1
	LSL      r0, r0, #8
	LSL      r0, r0, #0x10
	ASR      r0, r6, #0x16
	LSL      r0, r0, #0
	MOV      r3, #1
	MOV      r2, #0
	STR      r2, [r0, #4]
	LSL      r3, r3, #0xa
	STR      r3, [r0]
	STR      r2, [r0, #8]
	STR      r3, [r0, #0xc]
	ADD      r0, #0x10
	STMIA    r0!, {r2}
	STR      r2, [r0]
	BX       lr
	ADD      r2, r1, #0
	LDR      r3, [pc, #0x2a4]
	ADD      r2, #0x40
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x16
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x16
	LDR      r1, [r3, r1]
	LDR      r2, [r3, r2]
	ASR      r1, r1, #6
|unk_0803FCDE|
	INCBIN	baserom.gba_0x3fcde_0x3fce0.extracted
	STR      r1, [r0, #8]
	ASR      r2, r2, #6
	STMIA    r0!, {r2, r3}
	SUB      r0, #8
	STR      r2, [r0, #0xc]
	ADD      r0, #0x10
	MOV      r1, #0
	STMIA    r0!, {r1}
	STR      r1, [r0]
	BX       lr
	PUSH     {r4, r5, r6, r7}
	LDR      r1, [r1]
	ASR      r3, r1, #0xa
	ADD      r4, r3, #0
	LSL      r2, r3, #0x18
	LSR      r3, r2, #0x16
	LDR      r2, [pc, #0x270]
	LSL      r1, r1, #0x16
	LDR      r5, [r2, r3]
	ADD      r3, r4, #1
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x16
	LDR      r6, [r2, r3]
	LSR      r1, r1, #0x16
	MOV      r3, #1
	LSL      r3, r3, #0xa
	SUB      r3, r3, r1
	MUL      r5, r3
	MUL      r6, r1
	ADD      r5, r5, r6
	ADD      r4, #0x40
	LSL      r6, r4, #0x18
	LSR      r6, r6, #0x16
	LDR      r6, [r2, r6]
	ADD      r4, #1
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x16
	LDR      r2, [r2, r4]
	MUL      r3, r6
	MUL      r1, r2
	ADD      r1, r3, r1
	ASR      r5, r5, #0x10
|unk_0803FD34|
	INCBIN	baserom.gba_0x3fd34_0x3fd36.extracted
	ASR      r1, r1, #0x10
	STMIA    r0!, {r1, r3, r5}
	SUB      r0, #0xc
	STR      r1, [r0, #0xc]
	ADD      r0, #0x10
	MOV      r1, #0
	STMIA    r0!, {r1}
	STR      r1, [r0]
	POP      {r4, r5, r6, r7}
	BX       lr
	LDR      r2, [r1]
	LDR      r3, [r0, #0x10]
	LSL      r2, r2, #0xa
	ADD      r2, r3, r2
	STR      r2, [r0, #0x10]
	LDR      r1, [r1, #4]
	LDR      r2, [r0, #0x14]
	LSL      r1, r1, #0xa
	ADD      r1, r2, r1
	STR      r1, [r0, #0x14]
	BX       lr
	LDR      r2, [r1]
	LDR      r3, [r0, #0x10]
	LSL      r2, r2, #0xa
	SUB      r2, r3, r2
	STR      r2, [r0, #0x10]
	LDR      r1, [r1, #4]
	LDR      r2, [r0, #0x14]
	LSL      r1, r1, #0xa
	SUB      r1, r2, r1
	STR      r1, [r0, #0x14]
	BX       lr
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	SUB      sp, #0x30
	ADD      r4, r2, #0
	MOV      r2, #8
	ADD      r1, sp, #0x24
	ADD      r0, sp, #0xc
	LDR      r3, [pc, #0x1f0]
	BL       |inc_0x046118_0x049114| + 0xedc
	LDR      r1, [r5]
	LDR      r0, [r4]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r5, #4]
	ADD      r7, r5, #4
	ADD      r6, r4, #0
	ADD      r6, #8
	LDR      r0, [r4, #8]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r3, sp, #4
	LDMIA    r3!, {r2, r3}
	ADD      r0, r0, r2
	ADC      r1, r3
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0xc]
	LDR      r1, [r5]
	ADD      r0, r4, #4
	STR      r0, [sp, #0x2c]
	LDR      r0, [r4, #4]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r7]
	ADD      r0, r6, #4
	STR      r0, [sp, #0x28]
	LDR      r0, [r6, #4]
	BL       |inc_0x046118_0x049114| + 0xa58
	LDR      r2, [sp, #4]
	LDR      r3, [sp, #8]
	ADD      r0, r0, r2
	ADC      r1, r3
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x10]
	ADD      r0, r7, #4
	ADD      r7, r0, #0
	LDR      r1, [r5, #8]
	LDR      r0, [r4]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	ADD      r0, r7, #4
	STR      r0, [sp, #0x24]
	STR      r1, [sp, #8]
	LDR      r1, [r7, #4]
	LDR      r0, [r6]
	BL       |inc_0x046118_0x049114| + 0xa58
	LDR      r2, [sp, #4]
	LDR      r3, [sp, #8]
	ADD      r0, r0, r2
	ADC      r1, r3
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x14]
	LDR      r1, [r7]
	LDR      r0, [sp, #0x2c]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r7, r0, #0
	LDR      r0, [sp, #0x24]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	LDR      r0, [sp, #0x28]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	LDR      r3, [sp, #8]
	ADD      r0, r0, r7
	ADC      r1, r3
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x18]
	ADD      r5, #0x10
	LDR      r1, [r5]
	LDR      r0, [r4]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r5, #4]
	LDR      r0, [r6]
	ADD      r7, r5, #4
	BL       |inc_0x046118_0x049114| + 0xa58
	LDR      r2, [sp, #4]
	LDR      r3, [sp, #8]
	ADD      r0, r0, r2
	ADC      r1, r3
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	ADD      r4, #0x10
	LDR      r1, [r4]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x1c]
	LDR      r1, [r5]
	LDR      r0, [sp, #0x2c]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r5, r0, #0
	ADD      r6, r1, #0
	LDR      r1, [r7]
	LDR      r0, [sp, #0x28]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r0, r0, r5
	ADC      r1, r6
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	LDR      r1, [r4, #4]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x20]
	ADD      r0, sp, #0xc
	LDMIA    r0!, {r1, r2, r3}
	LDR      r4, [sp, #0x30]
	STMIA    r4!, {r1, r2, r3}
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r4!, {r1, r2, r3}
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
	LDR      r2, [r1]
	LDR      r3, [r0]
	MUL      r3, r2
	ASR      r3, r3, #0xa
	STR      r3, [r0]
	LDR      r3, [r0, #4]
	MUL      r3, r2
	ASR      r2, r3, #0xa
	STR      r2, [r0, #4]
	LDR      r2, [r1]
	LDR      r3, [r0, #8]
	MUL      r3, r2
	ASR      r3, r3, #0xa
	STR      r3, [r0, #8]
	LDR      r3, [r0, #0xc]
	MUL      r3, r2
	ASR      r2, r3, #0xa
	STR      r2, [r0, #0xc]
	LDR      r1, [r1]
	LDR      r2, [r0, #0x10]
	MUL      r2, r1
	ASR      r2, r2, #0xa
	STR      r2, [r0, #0x10]
	LDR      r2, [r0, #0x14]
	MUL      r2, r1
	ASR      r1, r2, #0xa
	STR      r1, [r0, #0x14]
	BX       lr
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #0x1c
	ADD      r4, r1, #0
	ADD      r1, sp, #0x1c
	MOV      r2, #8
	ADD      r0, sp, #4
	LDR      r3, [pc, #0x98]
	BL       |inc_0x046118_0x049114| + 0xedc
	LDR      r0, [r4]
	LDR      r1, [r4, #0xc]
	ADD      r3, r4, #4
	LDMIA    r3!, {r2, r3}
	MUL      r0, r1
	MUL      r2, r3
	ASR      r2, r2, #0xa
	ASR      r0, r0, #0xa
	ADD      r6, r4, #0
	ADD      r6, #8
	SUB      r5, r0, r2
	LSL      r1, r1, #0xa
	ADD      r7, r4, #4
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp, #4]
	LDR      r0, [r7]
|unk_0803FF08|
	INCBIN	baserom.gba_0x3ff08_0x3ff0a.extracted
	LSL      r1, r0, #0xa
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp, #8]
	LDR      r0, [r6]
|unk_0803FF16|
	INCBIN	baserom.gba_0x3ff16_0x3ff18.extracted
	LSL      r1, r0, #0xa
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp, #0xc]
	LDR      r0, [r4]
	LSL      r1, r0, #0xa
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp, #0x10]
	LDR      r1, [r4, #0x10]
	LDR      r2, [sp, #4]
|unk_0803FF32|
	INCBIN	baserom.gba_0x3ff32_0x3ff34.extracted
	MUL      r1, r2
	ADD      r0, r4, #0
	LDR      r2, [r4, #0x14]
	LDR      r4, [sp, #0xc]
	ASR      r3, r1, #0xa
	MUL      r2, r4
	ASR      r2, r2, #0xa
	SUB      r2, r3, r2
	STR      r2, [sp, #0x14]
	ADD      r0, #0x10
	ADD      r1, r0, #4
	LDR      r0, [r0]
	LDR      r3, [sp, #8]
|unk_0803FF4E|
	INCBIN	baserom.gba_0x3ff4e_0x3ff50.extracted
	MUL      r0, r3
	LDR      r1, [r1]
	LDR      r3, [sp, #0x10]
	ASR      r0, r0, #0xa
	MUL      r1, r3
	ASR      r1, r1, #0xa
	SUB      r0, r0, r1
	STR      r0, [sp, #0x18]
	ADD      r2, sp, #4
	ADD      r0, r2, #0
	LDMIA    r0!, {r1, r2, r3}
	LDR      r4, [sp, #0x1c]
	STMIA    r4!, {r1, r2, r3}
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r4!, {r1, r2, r3}
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	LDR      r4, [r5, #0x6c]
	LSR      r3, r7, #1
	LSL      r1, r4, #0x1d
	LSR      r5, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	SUB      sp, #0x18
	ADD      r4, r1, #0
	ADD      r1, sp, #0x18
	MOV      r2, #8
	MOV      r5, sp
	MOV      r0, sp
	LDR      r3, [pc, #0x54]
	BL       |inc_0x046118_0x049114| + 0xedc
	LDR      r1, [r4, #0xc]
	STR      r1, [sp]
	LDR      r1, [r4, #4]
|unk_0803FF98|
	INCBIN	baserom.gba_0x3ff98_0x3ff9a.extracted
	STR      r1, [sp, #4]
	LDR      r0, [r4, #8]
|unk_0803FF9E|
	INCBIN	baserom.gba_0x3ff9e_0x3ffa0.extracted
	STR      r0, [sp, #8]
	LDR      r0, [r4]
	STR      r0, [sp, #0xc]
	LDR      r1, [r4, #0x10]
	LDR      r2, [sp]
|unk_0803FFAA|
	INCBIN	baserom.gba_0x3ffaa_0x3ffac.extracted
	MUL      r1, r2
	ADD      r0, r4, #0
	LDR      r2, [r4, #0x14]
	LDR      r4, [sp, #8]
	ASR      r3, r1, #0xa
	MUL      r2, r4
	ASR      r2, r2, #0xa
	SUB      r2, r3, r2
	ADD      r0, #0x10
	ADD      r1, r0, #4
	STR      r2, [sp, #0x10]
	LDR      r0, [r0]
	LDR      r2, [sp, #4]
|unk_0803FFC6|
	INCBIN	baserom.gba_0x3ffc6_0x3ffc8.extracted
	MUL      r0, r2
	LDR      r1, [r1]
	LDR      r2, [sp, #0xc]
	ASR      r0, r0, #0xa
	MUL      r1, r2
	ASR      r1, r1, #0xa
	SUB      r0, r0, r1
	STR      r0, [sp, #0x14]
	LDMIA    r5!, {r0, r1, r2, r3}
	STMIA    r6!, {r0, r1, r2, r3}
	LDMIA    r5!, {r2, r3}
	STMIA    r6!, {r2, r3}
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
|loc_0803FFE4|
	DCW      0x0761
	DCW      0x0805
