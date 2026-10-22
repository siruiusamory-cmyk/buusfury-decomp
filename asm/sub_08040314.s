	CODE16
|sub_08040314|
	LDRB     r1, [r0]
	ADD      r1, #0x3f
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x19
	ADD      r0, r1, r0
	LDRH     r0, [r0, #8]
	BX       lr
	LDRB     r1, [r0]
	ADD      r1, #0x3f
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x19
	ADD      r0, r1, r0
	LDRH     r2, [r0, #8]
	MOV      r0, #0
	MOV      r3, #1
|loc_08040332|
	ADD      r1, r3, #0
	LSL      r1, r0
	AND      r1, r2
	BNE      |loc_08040344|
	ADD      r0, #1
	CMP      r0, #0xa
	BLT      |loc_08040332|
	MOV      r0, #0
	MVN      r0, r0
|loc_08040344|
	BX       lr
	LDRB     r1, [r0]
	ADD      r1, #0x3f
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x18
	ADD      r0, r1, r0
	ADD      r0, #0x80
	LDR      r0, [r0, #8]
	BX       lr
	LSL      r0, r0, #0
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	PUSH     {r4}
	MOV      r3, #1
	MOV      r1, #0
	STR      r1, [r0, #4]
	LSL      r3, r3, #0xa
	STR      r3, [r0]
	STR      r1, [r0, #8]
	STR      r1, [r0, #0xc]
	STR      r3, [r0, #0x10]
	STR      r1, [r0, #0x14]
	STR      r1, [r0, #0x18]
	STR      r1, [r0, #0x1c]
	STR      r3, [r0, #0x20]
	ADD      r0, #0x24
	STR      r1, [r0]
	STR      r1, [r0, #4]
	STR      r1, [r0, #8]
	POP      {r4}
	BX       lr
	LDR      r2, [r1]
	LDR      r3, [r0]
	MUL      r3, r2
	ASR      r3, r3, #0xa
	STR      r3, [r0]
	LDR      r3, [r0, #4]
	MUL      r3, r2
	ASR      r3, r3, #0xa
	STR      r3, [r0, #4]
	LDR      r3, [r0, #8]
	MUL      r3, r2
	ASR      r2, r3, #0xa
	STR      r2, [r0, #8]
	LDR      r2, [r1]
	LDR      r3, [r0, #0xc]
	MUL      r3, r2
	ASR      r3, r3, #0xa
	STR      r3, [r0, #0xc]
	LDR      r3, [r0, #0x10]
	MUL      r3, r2
	ASR      r3, r3, #0xa
	STR      r3, [r0, #0x10]
	LDR      r3, [r0, #0x14]
	MUL      r3, r2
	ASR      r2, r3, #0xa
	STR      r2, [r0, #0x14]
	LDR      r2, [r1]
	LDR      r3, [r0, #0x18]
	MUL      r3, r2
	ASR      r3, r3, #0xa
	STR      r3, [r0, #0x18]
	LDR      r3, [r0, #0x1c]
	MUL      r3, r2
	ASR      r3, r3, #0xa
	STR      r3, [r0, #0x1c]
	LDR      r3, [r0, #0x20]
	MUL      r3, r2
	ASR      r2, r3, #0xa
	STR      r2, [r0, #0x20]
	LDR      r1, [r1]
	LDR      r2, [r0, #0x24]
	MUL      r2, r1
	ASR      r2, r2, #0xa
	STR      r2, [r0, #0x24]
	LDR      r2, [r0, #0x28]
	MUL      r2, r1
	ASR      r2, r2, #0xa
	STR      r2, [r0, #0x28]
	LDR      r2, [r0, #0x2c]
	MUL      r2, r1
	ASR      r1, r2, #0xa
	STR      r1, [r0, #0x2c]
	BX       lr
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #0x54
	ADD      r4, r1, #0
	MOV      r1, sp
	MOV      r2, #0xc
	ADD      r1, r1, r2
	ADD      r1, #0x30
	MOV      r0, sp
	ADD      r0, r0, r2
	STR      r1, [sp, #0x50]
	LDR      r3, [pc, #0x38c]
	BL       |inc_0x046118_0x049114| + 0xedc
	ADD      r0, r4, #0
	ADD      r0, #0xc
	ADD      r5, r0, #0
	ADD      r0, #4
	STR      r0, [sp, #0x4c]
	LDR      r1, [r0]
	ADD      r0, #8
	ADD      r6, r0, #0
	ADD      r0, #8
	STR      r0, [sp, #0x48]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r7, r0, #0
	ADD      r0, r5, #0
	ADD      r0, #8
	STR      r0, [sp, #0x44]
	STR      r1, [sp, #8]
	LDR      r1, [r5, #8]
	ADD      r0, r6, #4
	STR      r0, [sp, #0x40]
	LDR      r0, [r6, #4]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r2, r7, #0
	LDR      r3, [sp, #8]
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0xc]
	LDR      r0, [sp, #0x44]
	LDR      r1, [r0]
	LDR      r0, [r6]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r1, [sp, #8]
	LDR      r1, [r5]
	ADD      r7, r0, #0
	LDR      r0, [sp, #0x48]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r2, r7, #0
	LDR      r3, [sp, #8]
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x18]
	LDR      r1, [r5]
	LDR      r0, [sp, #0x40]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r7, r0, #0
	LDR      r0, [sp, #0x4c]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	LDR      r0, [r6]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r2, r7, #0
	LDR      r3, [sp, #8]
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x24]
	LDR      r0, [sp, #0x40]
	LDR      r1, [r0]
	SUB      r0, r5, #4
	STR      r0, [sp, #0x3c]
	LDR      r0, [r4, #8]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	STR      r1, [sp, #8]
	LDR      r0, [sp, #0x48]
	ADD      r7, r4, #4
	LDR      r1, [r0]
	LDR      r0, [r4, #4]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r3, sp, #4
	LDMIA    r3!, {r2, r3}
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x10]
	LDR      r0, [sp, #0x48]
	LDR      r1, [r0]
	LDR      r0, [r4]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r6]
	LDR      r0, [sp, #0x3c]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r3, sp, #4
	LDMIA    r3!, {r2, r3}
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x1c]
	LDR      r1, [r6]
	LDR      r0, [r7]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	LDR      r0, [sp, #0x40]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	LDR      r0, [r4]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r3, sp, #4
	LDMIA    r3!, {r2, r3}
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x28]
	LDR      r1, [r7]
	LDR      r0, [sp, #0x44]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	LDR      r0, [sp, #0x3c]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	LDR      r0, [sp, #0x4c]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r3, sp, #4
	LDMIA    r3!, {r2, r3}
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0x3c]
	LDR      r1, [r0]
	LDR      r0, [r5]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r4]
	LDR      r0, [sp, #0x44]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r3, sp, #4
	LDMIA    r3!, {r2, r3}
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x20]
	LDR      r1, [r4]
	LDR      r0, [sp, #0x4c]
	LDR      r0, [r0]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r0, [sp, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r7]
	LDR      r0, [r5]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r3, sp, #4
	LDMIA    r3!, {r2, r3}
	BL       |inc_0x046118_0x049114| + 0xa7c
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x2c]
	LDR      r1, [r4]
	LDR      r0, [sp, #0xc]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r1, [sp, #8]
	LDR      r1, [r5]
	ADD      r7, r0, #0
	LDR      r0, [sp, #0x10]
	BL       |inc_0x046118_0x049114| + 0xa58
	LDR      r3, [sp, #8]
	ADD      r5, r0, r7
	ADC      r1, r3
	ADD      r7, r1, #0
	LDR      r1, [r6]
	LDR      r0, [sp, #0x14]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r2, r0, r5
	ADC      r1, r7
	ADD      r3, r1, #0
	ADR      r1, |loc_08040794|
	LDMIA    r1!, {r0, r1}
	BL       |inc_0x046118_0x049114| + 0xa8c
	ADD      r5, r0, #0
	ADD      r6, r1, #0
	LDR      r2, [sp, #0xc]
	BL       |inc_0x046118_0x049114| + 0xa40
	MOV      r7, #1
	LSL      r7, r7, #0x1d
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0xc]
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x10]
	BL       |inc_0x046118_0x049114| + 0xa40
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x10]
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x14]
	BL       |inc_0x046118_0x049114| + 0xa40
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x14]
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x18]
	BL       |inc_0x046118_0x049114| + 0xa40
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x18]
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x1c]
	BL       |inc_0x046118_0x049114| + 0xa40
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x1c]
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x20]
	BL       |inc_0x046118_0x049114| + 0xa40
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x20]
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x24]
	BL       |inc_0x046118_0x049114| + 0xa40
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x24]
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x28]
	BL       |inc_0x046118_0x049114| + 0xa40
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x28]
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x2c]
	BL       |inc_0x046118_0x049114| + 0xa40
	ADD      r2, r7, #0
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0x1e
	BL       |inc_0x046118_0x049114| + 0xb10
	STR      r0, [sp, #0x2c]
	ADD      r4, #0x24
	LDR      r1, [r4]
	LDR      r0, [sp, #0xc]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r7, r1, #0
	ADD      r6, r0, #0
	LDR      r1, [r4, #4]
	LDR      r0, [sp, #0x18]
	ADD      r5, r4, #4
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r0, r0, r6
	ADC      r1, r7
	STR      r1, [sp, #8]
	ADD      r7, r0, #0
	LDR      r1, [r4, #8]
	LDR      r0, [sp, #0x24]
	ADD      r6, r5, #4
	BL       |inc_0x046118_0x049114| + 0xa58
	LDR      r3, [sp, #8]
	ADD      r0, r0, r7
	ADC      r1, r3
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	BL       |inc_0x046118_0x049114| + 0xa6c
	STR      r0, [sp, #0x30]
	LDR      r1, [r4]
	LDR      r0, [sp, #0x10]
	BL       |inc_0x046118_0x049114| + 0xa58
	STR      r1, [sp, #4]
	LDR      r1, [r5]
	ADD      r7, r0, #0
	LDR      r0, [sp, #0x1c]
	BL       |inc_0x046118_0x049114| + 0xa58
	LDR      r3, [sp, #4]
	ADD      r7, r0, r7
	ADC      r1, r3
	STR      r1, [sp, #8]
	LDR      r1, [r6]
	LDR      r0, [sp, #0x28]
	BL       |inc_0x046118_0x049114| + 0xa58
	LDR      r3, [sp, #8]
	ADD      r0, r0, r7
	ADC      r1, r3
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	BL       |inc_0x046118_0x049114| + 0xa6c
	STR      r0, [sp, #0x34]
	LDR      r1, [r4]
	LDR      r0, [sp, #0x14]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r4, r0, #0
	ADD      r7, r1, #0
	LDR      r1, [r5]
	LDR      r0, [sp, #0x20]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r4, r0, r4
	ADC      r1, r7
	ADD      r5, r1, #0
	LDR      r1, [r6]
	LDR      r0, [sp, #0x2c]
	BL       |inc_0x046118_0x049114| + 0xa58
	ADD      r0, r0, r4
	ADC      r1, r5
	MOV      r2, #1
	LSL      r2, r2, #9
	BL       |inc_0x046118_0x049114| + 0xa00
	MOV      r2, #0xa
	BL       |inc_0x046118_0x049114| + 0xb10
	BL       |inc_0x046118_0x049114| + 0xa6c
	LDR      r2, [pc, #0x24]
	STR      r0, [sp, #0x38]
	MOV      r3, #0xc
	MOV      r1, sp
	STR      r2, [sp]
	LDR      r2, [sp, #0x50]
	ADD      r1, r1, r3
	LDR      r0, [sp, #0x54]
	BL       |inc_0x046118_0x049114| + 0xf00
	ADD      sp, #0x5c
	POP      {r4, r5, r6, r7, pc}
|loc_0804078E|
	DCW      0x0000
	DCW      0x0791,0x0805
|loc_08040794|
|unk_08040794|
; cited by 0x08040776 (a pc-relative load targets 0x0804079C)
	INCBIN	baserom.gba_0x40794_0x407a0.extracted
