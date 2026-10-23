	CODE16
|sub_08012846|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0xb0]
	SUB      sp, #0x24
	LDR      r0, [r0]
	LDR      r1, [sp, #0x24]
	ADD      r5, r0, #0
	LDR      r0, [r1]
	ADD      r5, #0x18
	MOV      r6, #0
	CMP      r0, #0
	BLE      |loc_080128F0|
|loc_0801285C|
	LDR      r1, [sp, #0x24]
	LSL      r0, r6, #2
	ADD      r0, r0, r1
	LDR      r4, [r0, #4]
	MOV      r3, #4
	LDRSH    r0, [r4, r3]
	MOV      r3, #6
	LDRSH    r1, [r4, r3]
	MOV      r3, #8
	LDRSH    r2, [r4, r3]
	MOV      r3, #0xa
	LDRSH    r7, [r4, r3]
	ADD      r0, #0xf
	STR      r0, [sp, #4]
	ADD      r1, #7
	STR      r7, [sp, #0x10]
	STR      r1, [sp, #8]
	ADD      r0, sp, #4
	STR      r2, [sp, #0xc]
	LDMIA    r0!, {r0, r1, r2, r3}
	ADD      r7, sp, #0x14
	STMIA    r7!, {r0, r1, r2, r3}
	LDR      r0, [sp, #0x14]
	LDR      r1, [r5, #8]
	SUB      r7, #0x10
	CMP      r0, r1
	BGE      |loc_080128E6|
	LDR      r0, [r5]
	LDR      r1, [sp, #0x1c]
	CMP      r0, r1
	BGE      |loc_080128E6|
	LDR      r0, [sp, #0x18]
	LDR      r1, [r5, #0xc]
	CMP      r0, r1
	BGE      |loc_080128E6|
	LDR      r0, [r5, #4]
	LDR      r1, [sp, #0x20]
	CMP      r0, r1
	BGE      |loc_080128E6|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_080128E6|
	LDR      r2, [sp, #0x28]
	LDR      r0, [r2]
	ADD      r1, r0, #1
	STR      r1, [r2]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LDR      r2, [sp, #0x28]
	LSL      r0, r0, #2
	ADD      r0, r0, r2
	ADD      r0, #4
	MOV      r1, #0
	STR      r1, [r0, #0x10]
	LDMIA    r7!, {r1, r2, r3, r7}
	STMIA    r0!, {r1, r2, r3, r7}
	SUB      r0, #0x10
	MOV      r1, #1
	STRB     r1, [r0, #0x14]
	STR      r4, [r0, #0x18]
	LDR      r2, [sp, #0x28]
	LDR      r0, [r2]
	CMP      r0, #0x10
	BEQ      |loc_080128F0|
|loc_080128E6|
	LDR      r1, [sp, #0x24]
	ADD      r6, #1
	LDR      r0, [r1]
	CMP      r0, r6
	BGT      |loc_0801285C|
|loc_080128F0|
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
|sub_080128F4|
|unk_080128F4|
	INCBIN	baserom.gba_0x128f4_0x128f6.extracted
|sub_080128F6|
	DCW      0x0804
	DCW      0x8000
|unk_080128FA|
	INCBIN	baserom.gba_0x128fa_0x128fe.extracted
	DCW      0x082b
