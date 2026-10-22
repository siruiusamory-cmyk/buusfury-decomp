	CODE16
|sub_08003D10|
	MOV      r1, #0
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r3, [r0]
	MOV      r1, #1
	ORR      r2, r3
	BNE      |loc_08003D2C|
	MOV      r1, #0
|loc_08003D2C|
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0]
|unk_08003D38|
	INCBIN	baserom.gba_0x3d38_0x3d3a.extracted
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r2, [r0]
	ADD      r1, r2, r1
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r2, [r0]
	SUB      r1, r2, r1
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r2, [r0]
	MUL      r2, r1
	STR      r2, [r0]
	BX       lr
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r4, r1, r0
	LDR      r0, [r4, #4]
	LDR      r1, [r4]
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [r4]
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r4, r1, r0
	LDR      r0, [r4, #4]
	LDR      r1, [r4]
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r1, [r4]
	POP      {r4, pc}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r3, [r0]
	MOV      r1, #1
	CMP      r3, r2
	BEQ      |loc_08003DC0|
	MOV      r1, #0
|loc_08003DC0|
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r3, [r0]
	MOV      r1, #1
	CMP      r3, r2
	BNE      |loc_08003DDA|
	MOV      r1, #0
|loc_08003DDA|
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r3, [r0]
	MOV      r1, #1
	CMP      r3, r2
	BGT      |loc_08003DF4|
	MOV      r1, #0
|loc_08003DF4|
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r3, [r0]
	MOV      r1, #1
	CMP      r3, r2
	BGE      |loc_08003E0E|
	MOV      r1, #0
|loc_08003E0E|
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r3, [r0]
	MOV      r1, #1
	CMP      r3, r2
	BLT      |loc_08003E28|
	MOV      r1, #0
|loc_08003E28|
	STR      r1, [r0]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r3, [r0]
	MOV      r1, #1
	CMP      r3, r2
	BLE      |loc_08003E42|
	MOV      r1, #0
|loc_08003E42|
	STR      r1, [r0]
	BX       lr
	LDR      r0, [r1]
	LDRB     r2, [r0]
	LDRB     r3, [r0, #1]
	LSL      r2, r2, #8
	ORR      r2, r3
	ADD      r0, r0, r2
	STR      r0, [r1]
	BX       lr
	LDR      r2, [r0]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #4]
	CMP      r0, #0
	LDR      r0, [r1]
	BNE      |loc_08003E76|
	LDRB     r2, [r0]
	LDRB     r3, [r0, #1]
	LSL      r2, r2, #8
	ORR      r2, r3
	ADD      r0, r0, r2
	STR      r0, [r1]
	BX       lr
|loc_08003E76|
	ADD      r0, #2
	STR      r0, [r1]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	BX       lr
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [r1]
	ADD      r4, r0, #0
	LDRB     r0, [r2]
	ADD      r2, #1
	STR      r2, [r1]
	LSL      r5, r0, #2
	LDR      r0, [pc, #0xac]
	LDR      r1, [r0, r5]
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4]
	LDR      r1, [pc, #0xa4]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	LDR      r1, [r1, r5]
	ADD      r0, #1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [r1]
	ADD      r4, r0, #0
	LDRB     r0, [r2]
	ADD      r2, #1
	STR      r2, [r1]
	LSL      r5, r0, #2
	LDR      r0, [pc, #0x7c]
	LDR      r1, [r0, r5]
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r1, [r0]
	ADD      r1, #1
	STR      r1, [r0]
	ADD      r0, r1, #0
	LDR      r1, [pc, #0x68]
	LDR      r1, [r1, r5]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [r1]
	ADD      r4, r0, #0
	LDRB     r0, [r2]
	ADD      r2, #1
	STR      r2, [r1]
	LSL      r5, r0, #2
	LDR      r0, [pc, #0x4c]
	LDR      r1, [r0, r5]
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4]
	LDR      r1, [pc, #0x44]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0]
	LDR      r1, [r1, r5]
	ADD      r0, #1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [r1]
	ADD      r4, r0, #0
	LDRB     r0, [r2]
	ADD      r2, #1
	STR      r2, [r1]
	LSL      r5, r0, #2
	LDR      r0, [pc, #0x20]
	LDR      r1, [r0, r5]
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4]
	LDR      r1, [pc, #0x18]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	LDR      r1, [r1, r5]
	SUB      r0, #1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
|sub_08003F40|
|unk_08003F40|
	INCBIN	baserom.gba_0x3f40_0x3f42.extracted
