	CODE16
|loc_0800CAFC|
		LDR r4, [r3, #0x24]
		ADD r3, r4, r3
	INCBIN  baserom.gba_0xcb00_0xcb02.extracted
|sub_0800CB02|
|unk_0800CB02|
	INCBIN	baserom.gba_0xcb02_0xcb06.extracted
	LSL      r0, r0, #0
	MOV      r5, #0x58
	LSR      r7, r0, #0x20
	BLS      |loc_0800CAB0|
	LSR      r7, r5, #1
	LDR      r3, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_0800CB2E|
	MOV      r0, #0x5c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800CB2E|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800CB2E|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800CEF4|
	LDR      r0, [pc, #0x294]
	MOV      r1, #0x38
	STR      r0, [r4]
	STRB     r1, [r4, #8]
	LDR      r1, [r5, #0xc]
	ADD      r0, r4, #0
	STR      r1, [r4, #4]
	LDR      r1, [r4, #0x24]
	LDR      r2, [r4, #0x2c]
	ADD      r0, #0x54
	ADD      r3, r1, r2
	ASR      r3, r3, #1
	STR      r3, [r4, #0x44]
	LDR      r3, [r4, #0x30]
	SUB      r1, r2, r1
	STR      r1, [r4, #0x34]
	STR      r3, [r4, #0x48]
	LDR      r1, [r4, #0x28]
	SUB      r2, r3, r1
	MOV      r1, #0
	STR      r1, [r4, #0x3c]
	STR      r2, [r4, #0x38]
	LSL      r2, r2, #7
	STR      r2, [r4, #0x40]
	MOV      r2, #0xf
	LSL      r2, r2, #0xc
	STR      r2, [r0]
	LDR      r2, [r4, #0x20]
	LDRB     r2, [r2, #0x16]
	CMP      r2, #0x28
	BNE      |loc_0800CB7C|
	MOV      r2, #0x37
	LSL      r2, r2, #0xb
	STR      r2, [r0]
|loc_0800CB7C|
	LDR      r2, [r4, #0x20]
	LDRB     r2, [r2, #0x16]
	CMP      r2, #0x3c
	BNE      |loc_0800CBA4|
	LDR      r2, [r4, #0x34]
	CMP      r2, #0x10
	BLE      |loc_0800CBA2|
	LDR      r2, [r4, #0x30]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [r4, #0x28]
	ADD      r2, r2, r3
	ASR      r2, r2, #2
	STR      r2, [r4, #0x48]
	LDR      r2, [r4, #0x40]
	LSR      r3, r2, #0x1f
	ADD      r2, r3, r2
	ASR      r2, r2, #1
	STR      r2, [r4, #0x40]
|loc_0800CBA2|
	STR      r1, [r0]
|loc_0800CBA4|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x1c]
	SUB      sp, #0x20
	CMP      r0, #0
	BNE      |Math_Divide2|
	ADD      sp, #0x20
	POP      {r4, pc}
