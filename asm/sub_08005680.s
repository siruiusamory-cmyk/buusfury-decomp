	CODE16
|sub_08005680|
	MOV      r1, #0
	STR      r1, [r0, #8]
	MOV      r1, #0xf0
	MOV      r2, #0xa0
	ADD      r6, sp, #4
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r3, #1
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [r4, #0x14]
	BL       |loc_08006718|
	MOV      r3, #0x20
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [r4, #0x28]
	BL       |loc_08005578|
	LDR      r2, [r4, #0x28]
	MOV      r3, #0x54
	ADD      r1, r6, #0
	ADD      r2, #1
	ADD      r0, r5, #0
	BL       |loc_08005578|
	MOV      r3, #0xd0
	MOV      r2, #0x50
	MOV      r1, #0x14
	ADD      r0, r6, #0
	BL       |loc_08005154|
	MOV      r3, #0x74
	MOV      r2, #0x2e
	MOV      r1, #0xdb
	ADD      r0, r6, #0
	BL       |loc_080051B0|
	LDR      r1, [pc, #0x40]
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x30
	ADD      r0, r5, #0
	BL       |sub_080054BA|
	MOV      r1, #0
	ADD      r0, sp, #4
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x38
	POP      {r4, r5, r6, pc}
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	STR      r7, [sp, #0xa0]
	LSR      r4, r0, #0x20
	STR      r4, [r3, #0x1c]
	LSR      r5, r0, #0x20
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	LDR      r4, [r5]
	LSR      r5, r0, #0x20
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
|loc_08005700|
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r2, r7, #0
	LSL      r5, r4, #0
	LSL      r0, r6, #0
	LSL      r2, r6, #0
	LSL      r4, r4, #1
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	ADD      r0, #0xff
	ADD      r0, #1
	MOV      r1, #0
	CMP      r2, #2
	BEQ      |sub_08005732|
	CMP      r2, #3
	BNE      |loc_0800572E|
	LDR      r2, [r0, #0xc]
	CMP      r2, #2
	BGE      |loc_0800572C|
	ADD      r2, #1
	STR      r2, [r0, #0xc]
|loc_0800572C|
	STR      r1, [r0, #0x10]
|loc_0800572E|
	MOV      r0, #0
	BX       lr
