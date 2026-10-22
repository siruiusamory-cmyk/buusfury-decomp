	CODE16
|sub_0804841E|
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_08048424|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
|unk_08048430|
	INCBIN	baserom.gba_0x48430_0x48432.extracted
	LSR      r4, r0, #0x20
	ADD      r4, r7, #0
	LSL      r0, r0, #0xc
	ADD      r3, sp, #0x1b0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x34]
	MOV      r2, #0x41
	LSL      r2, r2, #3
	MOV      r0, #0
	STR      r0, [r1, #4]
	ADD      r2, r1, r2
	STR      r0, [r2]
	LDR      r2, [pc, #0x2c]
	ADD      r2, r1, r2
	STR      r0, [r2]
	MOV      r2, #0x61
	LSL      r2, r2, #4
	ADD      r2, r1, r2
	STR      r0, [r2]
	MOV      r2, #0x2f
	LSL      r2, r2, #6
	ADD      r1, r1, r2
	STR      r0, [r1, #0x38]
	LDR      r1, [pc, #0x1c]
	LDR      r2, [pc, #0x18]
|loc_08048464|
	STR      r1, [r2]
	LDR      r1, [pc, #0xc]
	SUB      r1, #8
	STR      r0, [r1, #4]
	LDR      r0, [pc, #0x14]
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r4, r1, #1
	LSL      r0, r0, #0xc
	LSL      r4, r1, #0x10
	LSL      r0, r0, #0
	CMP      r2, #0x4c
	LSL      r0, r0, #0xc
	STR      r2, [sp, #0x1d0]
	LSR      r4, r0, #0x20
	STR      r6, [sp, #0x1c0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
|loc_0804848C|
	STR      r0, [r1]
	BX       lr
|sub_08048490|
|unk_08048490|
	INCBIN	baserom.gba_0x48490_0x48492.extracted
