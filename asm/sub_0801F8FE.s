	CODE16
|sub_0801F8FE|
	STR      r1, [r0, #8]
	B        |loc_0801F90C|
|loc_0801F902|
	LDR      r0, [r5, #0x18]
	MOV      r1, #0
	STR      r1, [r0, #8]
	LDR      r0, [r5, #0x1c]
	STR      r1, [r0, #8]
|loc_0801F90C|
	MOV      r3, #0x70
	MOV      r2, #0x37
	MOV      r1, #0x75
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x5058
	MOV      r0, #2
	STRB     r0, [r4, #3]
	LDR      r0, [pc, #0x234]
	STRB     r7, [r4, #2]
	STR      r0, [r4, #0x20]
	MOV      r1, #0
	STRB     r1, [r4]
	MOV      r0, #0xe
	STRB     r0, [r4, #1]
	LDR      r0, [pc, #0x22c]
	MOV      r7, #0
	LDR      r0, [r0, #8]
	STR      r0, [r4, #0xc]
|loc_0801F932|
	LDR      r0, [r5, #0x20]
	LDR      r1, [sp]
	ADD      r0, r0, r7
	LDR      r1, [r1]
	CMP      r1, r0
	BLE      |loc_0801F960|
	LSL      r1, r7, #3
	SUB      r1, r1, r7
	LSL      r1, r1, #1
	ADD      r1, #0x31
	STR      r1, [r4, #8]
	MOV      r2, #0x16
	STR      r2, [r4, #4]
	LDR      r1, [sp]
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	ADD      r0, #4
	ADD      r1, r4, #0
	BL       |sub_0801F810|
	ADD      r7, #1
	CMP      r7, #6
	BLT      |loc_0801F932|
|loc_0801F960|
	MOV      r0, #0x31
	STR      r0, [r4, #8]
	MOV      r0, #0xff
	MOV      r7, #0x8c
	LDR      r1, [pc, #0x1cc]
	STR      r7, [r4, #4]
	ADD      r0, #0x41
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r5, #0
|loc_0801F978|
	LDR      r0, [r6]
	CMP      r0, r5
	BLE      |loc_0801F99C|
	LSL      r0, r5, #3
	SUB      r0, r0, r5
	LSL      r0, r0, #1
	ADD      r0, #0x3f
	STR      r0, [r4, #8]
	LSL      r0, r5, #3
	ADD      r0, r0, r6
	ADD      r0, #4
	ADD      r1, r4, #0
	STR      r7, [r4, #4]
	BL       |sub_0801F810|
	ADD      r5, #1
	CMP      r5, #6
	BLT      |loc_0801F978|
|loc_0801F99C|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r4, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	MOV      r0, sp
	MOV      r5, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r3, #1
	MOV      r2, #0x4f
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x65c0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_0801F882|
	LDR      r1, [pc, #0x194]
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LSL      r0, r2, #3
	ADD      r4, r0, r1
	LDR      r5, [r4, #4]
	ADD      r0, r4, #4
	SUB      r3, r5, r3
	STR      r3, [r4, #4]
	BNE      |loc_0801F9FC|
	LDR      r3, [r1]
	SUB      r3, #1
	STR      r3, [r1]
	SUB      r1, r3, r2
	BEQ      |loc_0801F9FC|
	LSL      r2, r1, #3
	ADD      r1, r4, #0
	ADD      r1, #0xc
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801F9FC|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r2, #0
	LSL      r2, r3, #3
	ADD      r4, r2, r5
	LDR      r6, [sp, #0x18]
	STR      r4, [sp]
	ADD      r7, r3, #0
	ADD      r3, r6, #0
	ADD      r4, #4
	ADD      r2, r4, #0
	BL       |sub_0801F3DC|
	CMP      r0, #0
	BEQ      |loc_0801FA3A|
	LDR      r0, [r4]
	SUB      r0, r0, r6
	STR      r0, [r4]
	BNE      |loc_0801FA3A|
	LDR      r0, [r5]
	SUB      r0, #1
	STR      r0, [r5]
	SUB      r0, r0, r7
	BEQ      |loc_0801FA3A|
	LDR      r1, [sp]
	LSL      r2, r0, #3
	ADD      r1, #0xc
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801FA3A|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r1, [pc, #0x114]
	LDR      r0, [pc, #0x11c]
	LDR      r1, [r1, #4]
	ADD      r4, r5, #0
	ADD      r7, r1, r0
	MOV      r0, #0x5d
	LSL      r0, r0, #5
	ADD      r4, #0xff
	ADD      r4, #1
	ADD      r6, r5, r0
	CMP      r2, #0
	SUB      sp, #0xc
	BEQ      |sub_0801FA88|
	LDR      r1, [pc, #0x108]
	CMP      r2, #2
	BEQ      |loc_0801FB1C|
	CMP      r2, #3
	BNE      |loc_0801FA82|
	LDR      r0, [r6]
	LDR      r2, [r4, #0x28]
	SUB      r0, #1
	CMP      r0, r2
	BLE      |loc_0801FA7E|
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0x28]
	ADD      r0, #1
	STR      r0, [r4, #0x28]
|loc_0801FA7E|
	MOV      r2, #0
	STR      r2, [r4, #0x10]
|loc_0801FA82|
	MOV      r0, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
