	CODE16
|loc_0803656C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0, #0x10]
	SUB      sp, #0x3c
	STR      r1, [sp, #0x30]
	LDR      r1, [r0, #0x10]
	MOV      r3, #4
	LDRSH    r2, [r1, r3]
	MOV      r3, #6
	LDRSH    r5, [r1, r3]
	MOV      r3, #8
	LDRSH    r6, [r1, r3]
	MOV      r3, #0xa
	LDRSH    r1, [r1, r3]
	ADD      r6, #0xf
	STR      r6, [sp, #0x10]
	STR      r5, [sp, #0xc]
	ADD      r1, #7
	STR      r1, [sp, #0x14]
	ADD      r5, sp, #8
	STR      r2, [sp, #8]
	LDMIA    r5!, {r1, r2, r3, r5}
	ADD      r6, sp, #0x18
	STMIA    r6!, {r1, r2, r3, r5}
	LDR      r1, [sp, #0x18]
	LDR      r2, [sp, #0x20]
	LDR      r3, [sp, #0x24]
	ADD      r2, r1, r2
	LDR      r1, [sp, #0x1c]
	STR      r2, [sp, #0x10]
	ADD      r1, r1, r3
	STR      r1, [sp, #0x14]
	ASR      r1, r1, #1
	ASR      r2, r2, #1
	STR      r1, [sp, #0x14]
	STR      r1, [sp, #0x2c]
	LSL      r1, r4, #3
	STR      r2, [sp, #0x10]
	STR      r2, [sp, #0x28]
	LDR      r2, [pc, #0x168]
	MOV      ip, r1
	ADD      ip, r2
	LDR      r1, [pc, #0x164]
	LDR      r2, [pc, #0x148]
	MOV      lr, r1
	LDR      r1, [r2, #8]
	ADD      r3, r0, #0
	ADD      r3, #0x80
	LDR      r1, [r1]
	MOV      r5, #0
	CMP      r1, #0
	STR      r3, [sp, #0x38]
	BLE      |loc_0803668E|
|loc_080365D6|
	LDR      r1, [pc, #0x134]
	LSL      r2, r5, #2
	LDR      r1, [r1, #8]
	ADD      r1, r2, r1
	LDR      r4, [r1, #4]
	LDR      r1, [sp, #0x30]
	CMP      r4, r1
	BEQ      |loc_08036682|
	MOV      r3, #4
	LDRSH    r1, [r4, r3]
	MOV      r3, #6
	LDRSH    r2, [r4, r3]
	MOV      r3, #8
	LDRSH    r6, [r4, r3]
	MOV      r3, #0xa
	LDRSH    r7, [r4, r3]
	ADD      r6, #0xf
	STR      r6, [sp, #8]
	ADD      r3, r7, #7
	STR      r3, [sp, #0xc]
	MOV      r6, sp
	STR      r1, [sp]
	STR      r2, [sp, #4]
	LDMIA    r6!, {r1, r2, r3, r6}
	ADD      r7, sp, #0x10
	STMIA    r7!, {r1, r2, r3, r6}
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x18]
	LDR      r3, [sp, #0x1c]
	ADD      r2, r1, r2
	LDR      r1, [sp, #0x14]
	STR      r2, [sp, #8]
	ADD      r1, r1, r3
	STR      r1, [sp, #0xc]
	ASR      r1, r1, #1
	ASR      r2, r2, #1
	STR      r1, [sp, #0xc]
	STR      r1, [sp, #0x24]
	ADD      r1, r2, #0
	STR      r2, [sp, #8]
	STR      r2, [sp, #0x20]
	LDR      r2, [sp, #0x28]
	LDR      r3, [sp, #0x2c]
	SUB      r1, r1, r2
	LDR      r2, [sp, #0x24]
	STR      r1, [sp, #0x18]
	SUB      r2, r2, r3
	STR      r2, [sp, #0x1c]
	MOV      r3, ip
	LDR      r3, [r3]
	ADD      r6, r1, #0
	MUL      r6, r3
	STR      r3, [sp, #0x34]
	MOV      r3, ip
	LDR      r3, [r3, #4]
	ADD      r7, r2, #0
	MUL      r7, r3
	MUL      r1, r3
	LDR      r3, [sp, #0x34]
	ADD      r6, r6, r7
	MUL      r2, r3
	ADD      r1, r1, r2
	BPL      |loc_08036656|
|unk_08036654|
	INCBIN	baserom.gba_0x36654_0x36656.extracted
