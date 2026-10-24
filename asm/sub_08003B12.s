	CODE16
|sub_08003B12|
	ADD      r6, r3, #0
	LSL      r3, r6, #4
	SUB      r6, r3, r6
	MOV      r3, #0x13
	LSL      r3, r3, #6
	ADD      r3, r0, r3
	STR      r1, [r3, #0x2c]
	STR      r2, [r3, #0x28]
	MOV      r1, #0x4f
	LSL      r6, r6, #2
	LSL      r1, r1, #4
	STR      r4, [r3, #0x24]
	STR      r5, [r3, #0x20]
	ADD      r0, r0, r1
	MOV      r1, #0
	STR      r6, [r3, #0x1c]
|loc_08003B32|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08003B32|
	LDR      r0, [pc, #0x10c]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_08003B46|
	BL       |loc_0801064C|
|loc_08003B46|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	CMP      r4, #0xc8
	BLE      |loc_08003B66|
	MOV      r4, #0xc8
|loc_08003B66|
	MOV      r3, #0x68
	LDR      r0, [pc, #0xd8]
	MUL      r1, r3
	LDR      r0, [r0, #0x14]
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r5, r0, r1
	ADD      r0, r5, #0
	BL       |Stats_GetLevel|
	CMP      r0, r4
	BGE      |loc_08003B92|
	ADD      r2, r4, #0
	ADD      r1, r0, #0
	ADD      r0, r5, #0
	BL       |Stats_ApplyLevelUp|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |Stats_SetLevel|
|loc_08003B92|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r2, [r0]
	SUB      sp, #0x10
	SUB      r2, #1
	LSL      r1, r2, #2
	STR      r2, [r0]
	SUB      r2, #1
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LSL      r3, r2, #2
	STR      r2, [r0]
	ADD      r3, r3, r0
	LDR      r3, [r3, #4]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	STR      r2, [sp, #0xc]
	LDR      r2, [r0]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #4]
	MOV      r2, #1
	STR      r0, [sp, #8]
	LDR      r0, [pc, #0x78]
	LDR      r4, [r0, #0x10]
	STR      r1, [sp]
	MOV      r1, #0
	STR      r2, [sp, #4]
	ADD      r2, sp, #8
	MOV      r0, #0
	BL       |inc_0x351c0_0x3d4d0| + 0x568a
	ADD      r2, r0, #0
	LDRB     r1, [r0, #4]
	ADD      r0, r4, #0
	BL       |loc_0800927E|
	ADD      sp, #0x10
	POP      {r4, pc}
	LDR      r1, [pc, #0x60]
	LDR      r3, [r1]
	LDR      r1, [r0]
	ADD      r2, r1, #1
	STR      r2, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r3, [r0, #4]
	BX       lr
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r1, [pc, #0x40]
	SUB      r2, #1
	LDR      r1, [r1, #0x14]
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #4]
	LSL      r2, r0, #4
	SUB      r2, r2, r0
	MOV      r0, #0x13
	LSL      r0, r0, #6
	ADD      r0, r1, r0
	LSL      r2, r2, #2
	STR      r2, [r0, #0x1c]
	MOV      r2, #0
	STR      r2, [r0, #0x20]
	STR      r2, [r0, #0x24]
	STR      r2, [r0, #0x28]
	STR      r2, [r0, #0x2c]
	MOV      r0, #0x4f
	LSL      r0, r0, #4
	ADD      r0, r1, r0
	MOV      r1, #1
|loc_08003C2E|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08003C2E|
	LDR      r0, [pc, #0x10]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_08003C42|
	BL       |loc_0801064C|
|loc_08003C42|
	POP      {r3, pc}
|sub_08003C44|
|unk_08003C44|
	INCBIN	baserom.gba_0x3c44_0x3c46.extracted
