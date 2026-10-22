	CODE16
|sub_080482BE|
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x70]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0x80]
	LDR      r1, [pc, #0x84]
	PUSH     {r4}
	STR      r0, [r1]
	LDR      r0, [pc, #0x7c]
	LDR      r2, [pc, #0x84]
	ADD      r0, #0x10
	STR      r2, [r0]
	MOV      r0, #3
	ADD      r1, #0x10
	STRB     r0, [r1, #4]
	ADD      r1, #8
	STR      r2, [r1]
	MOV      r2, #4
	STRB     r2, [r1, #4]
	LDR      r3, [pc, #0x68]
	LDR      r1, [pc, #0x70]
	ADD      r3, #0x20
	STR      r1, [r3]
	STRB     r0, [r3, #4]
	ADD      r3, #8
	STR      r1, [r3]
	STRB     r2, [r3, #4]
	LDR      r1, [pc, #0x58]
	LDR      r2, [pc, #0x64]
	ADD      r1, #0x30
	STRB     r0, [r1, #4]
	STR      r2, [r1]
	MOV      r1, #2
	ADD      r3, #0x10
	STRB     r1, [r3, #4]
	STR      r2, [r3]
	LDR      r2, [pc, #0x44]
	LDR      r4, [pc, #0x48]
	ADD      r2, #4
	STR      r4, [r2]
	MOV      r2, #5
	ADD      r3, #8
	STRB     r2, [r3, #4]
	LDR      r2, [pc, #0x4c]
	STR      r2, [r3]
	LDR      r2, [pc, #0x34]
	ADD      r3, #8
	ADD      r2, #0x48
	STRB     r0, [r2, #4]
	LDR      r2, [pc, #0x44]
	STR      r2, [r3]
	LDR      r2, [pc, #0x28]
	ADD      r2, #0x50
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0x3c]
	STR      r1, [r2]
	LDR      r1, [pc, #0x3c]
	SUB      r2, #0x48
	STR      r1, [r2]
	LDR      r1, [pc, #0x3c]
	ADD      r2, #4
	STR      r1, [r2]
	LDR      r1, [pc, #0x10]
	ADD      r1, #0x58
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x34]
	STR      r0, [r1]
	POP      {r4}
	BX       lr
|loc_08048346|
	DCW      0x0000
	DCW      0x985c,0x0804,0x1b00,0x0300,0xa188,0x0804,0xd784,0x0804
	DCW      0xc720,0x0804,0xe0ac
|loc_0804835E|
	LSR      r4, r0, #0x20
	ADR      r7, |loc_08048424|
	LSR      r4, r0, #0x20
	LDR      r6, [sp, #0x100]
	LSR      r4, r0, #0x20
	STMIA    r3!, {r2, r3, r4, r6}
	LSR      r4, r0, #0x20
	ADR      r1, |loc_08048620|
	LSR      r4, r0, #0x20
	ADR      r7, |loc_08048564|
	LSR      r4, r0, #0x20
	ADR      r1, |loc_080486B8|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0x48]
	LDR      r1, [pc, #0x4c]
	LDR      r3, [pc, #0x58]
	STR      r0, [r1]
	ADD      r1, #4
	LDR      r0, [pc, #0x48]
	ADD      r2, r1, #4
	STR      r0, [r1]
	LDR      r0, [pc, #0x48]
	LDR      r1, [pc, #0x44]
	STR      r0, [r2]
	LDR      r0, [pc, #0x4c]
	ADD      r2, #4
	STR      r0, [r2]
	LDR      r0, [pc, #0x48]
	ADD      r2, #4
	STR      r0, [r2]
	LDR      r0, [pc, #0x48]
	ADD      r2, #4
	STR      r0, [r2]
	LDR      r0, [pc, #0x44]
	ADD      r2, #4
	STR      r0, [r2]
	ADD      r0, r2, #4
	STR      r1, [r0]
	ADD      r0, #4
	STR      r3, [r0]
	LDR      r1, [pc, #0x18]
	LDR      r0, [pc, #0x38]
	ADD      r1, #0x24
	STR      r0, [r1]
	LDR      r0, [pc, #0x38]
	ADD      r1, #4
	STR      r0, [r1]
	LDR      r0, [pc, #0x34]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_080483C4|
	DCW      0xc464
	DCW      0x0804,0x1b60,0x0300,0xda40,0x0804,0xdf3c,0x0804,0xe110
	DCW      0x0804,0xda50,0x0804,0xe194,0x0804,0xc474,0x0804,0xcd8c
	DCW      0x0804,0xd868,0x0804,0xe054,0x0804,0xe40c,0x0804,0xe374
|loc_080483F6|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
	STR      r0, [r1]
	BX       lr
|sub_08048400|
|unk_08048400|
	INCBIN	baserom.gba_0x48400_0x48402.extracted
