	CODE16
|sub_0801F44E|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x360]
	ADD      r6, #0x11
	SUB      sp, #0x10
	MOV      r1, #2
	STRB     r1, [r6, #4]
	LDR      r1, [r0, #0xc]
	ADD      r7, r5, #0
	ADD      r1, #0xe4
	STR      r1, [sp, #0xc]
	LDR      r0, [r1]
	ADD      r7, #0xff
	ADD      r7, #0x2d
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_0801F49E|
|loc_0801F474|
	MOV      r0, #0
	ADD      r3, sp, #0
	STRB     r0, [r3, #4]
	LDR      r1, [sp, #0xc]
	LSL      r0, r4, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	ADD      r1, r7, #0
	STRB     r0, [r3, #5]
	MOV      r3, #1
	ADD      r0, r5, #0
	MOV      r2, sp
	BL       |sub_0801F3DC|
	MOV      r0, #0
	STRB     r0, [r6, #4]
	LDR      r1, [sp, #0xc]
	ADD      r4, #1
	LDR      r0, [r1]
	CMP      r0, r4
	BGT      |loc_0801F474|
|loc_0801F49E|
	MOV      r4, #0
|loc_0801F4A0|
	MOV      r0, #0x34
	LDR      r1, [pc, #0x318]
	MUL      r0, r4
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r0, r0, #0x1f
	BNE      |loc_0801F4D6|
	MOV      r0, #1
	ADD      r3, sp, #0
	STRB     r0, [r3, #4]
	LDR      r0, [pc, #0x300]
	STRB     r4, [r3, #5]
	LDR      r0, [r0, #0xc]
	ADD      r1, r7, #0
	ADD      r0, r0, r4
	STR      r0, [sp, #8]
	LDRB     r3, [r0, #2]
	ADD      r0, r5, #0
	MOV      r2, sp
	BL       |sub_0801F3DC|
	LDR      r0, [sp, #8]
	LDRB     r0, [r0, #2]
	CMP      r0, #0
	BEQ      |loc_0801F4D6|
	MOV      r0, #0
	STRB     r0, [r6, #4]
|loc_0801F4D6|
	ADD      r4, #1
	CMP      r4, #0x53
	BLT      |loc_0801F4A0|
	LDR      r0, [pc, #0x2d8]
	LDR      r1, [pc, #0x2e0]
	LDR      r0, [r0, #0xc]
	ADD      r0, r0, r1
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_0801F502|
	MOV      r1, #2
	ADD      r3, sp, #0
	STRB     r1, [r3, #4]
	MOV      r4, #0
	STRB     r4, [r3, #5]
	LDR      r3, [r0]
	ADD      r1, r7, #0
	ADD      r0, r5, #0
	MOV      r2, sp
	BL       |sub_0801F3DC|
	STRB     r4, [r6, #4]
|loc_0801F502|
	ADD      sp, #0x10
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BNE      |loc_0801F51A|
	LDR      r0, [pc, #0x2b4]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0801F51A|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_0801F51A|
	LDR      r0, [pc, #0x2ac]
	MOV      r1, #0
	STMIA    r4!, {r0, r1}
	SUB      r4, #8
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #8]
	LDR      r2, [pc, #0x29c]
	STR      r1, [r0, #0x10]
	STR      r2, [r4]
	MOV      r2, #0xff
	ADD      r2, #0x2d
	STR      r1, [r2, r4]
	MOV      r2, #0x5d
	LSL      r2, r2, #5
	ADD      r2, r4, r2
	STR      r1, [r2]
	LDR      r2, [pc, #0x28c]
	ADD      r2, r4, r2
	STR      r1, [r2]
	STR      r1, [r0, #0x20]
	STR      r1, [r0, #0x24]
	STR      r1, [r0, #0x28]
	ADD      r0, r4, #0
	BL       |sub_0801F44E|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_0801F556|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x5d
	LSL      r0, r0, #5
	ADD      r7, r5, r0
	LDR      r2, [pc, #0x254]
	LDR      r0, [r7]
	LDR      r2, [r2, #0xc]
	LDR      r1, [pc, #0x258]
	MOV      r4, #0
	ADD      r6, r2, r1
	CMP      r0, #0
	BLE      |loc_0801F5BA|
|loc_0801F570|
	LSL      r0, r4, #3
	ADD      r0, r0, r7
	ADD      r0, #4
	LDRB     r1, [r0, #4]
	CMP      r1, #0
	BEQ      |sub_0801F58C|
	CMP      r1, #1
	BEQ      |loc_0801F598|
	CMP      r1, #2
	BNE      |loc_0801F5B2|
	LDR      r0, [r0]
	LDR      r1, [r6]
	SUB      r0, r1, r0
	B        |sub_0801F5AA|
