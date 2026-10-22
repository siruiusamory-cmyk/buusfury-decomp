	CODE16
|sub_08000662|
	LSL      r0, r0, #0xc
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	LSL      r4, r6, #0x13
	LSL      r0, r0, #0
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	LDR      r1, [pc, #0x25c]
	MOV      r3, #0x68
	LDR      r1, [r1, #0x14]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1, #0x14]
	LDR      r2, [pc, #0x24c]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRH     r1, [r1, #4]
	LDR      r2, [pc, #0x244]
	LSL      r1, r1, #2
	LDR      r2, [r2, r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r4}
	LDR      r1, [r0]
	MOV      r3, #0x68
	SUB      r1, #1
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	STR      r1, [r0]
	LDR      r4, [r2, #4]
	LDR      r2, [pc, #0x218]
	MUL      r3, r4
	LDR      r2, [r2, #0x14]
	ADD      r2, r3, r2
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r2, r2, r3
	LDRB     r2, [r2, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [pc, #0x208]
	LSL      r2, r2, #3
	ADD      r2, r2, r3
	LDRH     r2, [r2, #2]
	LDR      r3, [pc, #0x204]
	LSL      r2, r2, #2
	LDR      r2, [r3, r2]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r4}
	BX       lr
	LDR      r1, [pc, #0x1f4]
	LDR      r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1d4]
	MOV      r3, #0x68
	LDR      r0, [r0, #0x14]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	BL       |loc_080135D2|
	LDR      r1, [r4]
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r1, r1, r4
	STR      r2, [r4]
	STR      r0, [r1, #4]
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r4, r1, r0
	LDR      r0, [r4]
	BL       |inc_0x03d784_0x041118| + 0x2348
	STR      r0, [r4]
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LDR      r3, [pc, #0x1a8]
	LSL      r1, r1, #2
	ADD      r4, r1, r0
	LDR      r0, [r4]
	MUL      r0, r3
	ASR      r0, r0, #8
	BL       |inc_0x03d784_0x041118| + 0x235a
	STR      r0, [r4]
	POP      {r4, pc}
	PUSH     {r4}
	LDR      r1, [r0]
	LDR      r4, [pc, #0x194]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	LSL      r3, r1, #2
	STR      r1, [r0]
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x16
	ADD      r3, r3, r0
	LDR      r3, [r3, #4]
	LDR      r2, [r4, r2]
	MUL      r2, r3
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ASR      r2, r2, #0x10
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r4}
	BX       lr
	PUSH     {r4}
	LDR      r1, [r0]
	LDR      r4, [pc, #0x164]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	ADD      r2, #0x40
	LSL      r2, r2, #0x18
	LSL      r3, r1, #2
	STR      r1, [r0]
	ADD      r3, r3, r0
	LSR      r2, r2, #0x16
	LDR      r2, [r4, r2]
	LDR      r3, [r3, #4]
	MUL      r2, r3
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ASR      r2, r2, #0x10
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r4}
	BX       lr
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r4, r1, r0
	LDR      r0, [pc, #0x118]
	LDR      r1, [r4]
	LDR      r0, [r0, #0x14]
	BL       |loc_08004364|
	STR      r0, [r4]
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r4, r1, r0
	LDR      r0, [pc, #0x100]
	LDR      r1, [r4]
	LDR      r0, [r0, #0x14]
	BL       |loc_08004364|
	MOV      r1, #1
	SUB      r0, r1, r0
	STR      r0, [r4]
	POP      {r4, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0xe0]
	LDR      r0, [r0, #0x14]
	BL       |sub_08004380|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0xc8]
	LDR      r0, [r0, #0x14]
	BL       |loc_08004396|
	POP      {r3, pc}
	LDR      r1, [pc, #0xc0]
	PUSH     {r4, lr}
	LDR      r4, [r1, #4]
	LDR      r1, [r0]
	MOV      r2, #0x40
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0xc4]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LDR      r0, [pc, #0xbc]
	MOV      r3, #0
	ADD      r0, r4, r0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LDR      r4, [pc, #0xac]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x7c]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r3, [pc, #0x8c]
	LSL      r1, r1, #2
	ADD      r1, r1, r3
	LDR      r0, [r0, #4]
	MOV      r3, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, pc}
	LDR      r1, [pc, #0x64]
	PUSH     {r3, lr}
	LDR      r2, [r1, #4]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x68]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LDR      r0, [pc, #0x64]
	ADD      r0, r2, r0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	POP      {r3, pc}
	LDR      r0, [pc, #0x3c]
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x54]
	ADD      r0, r0, r1
	BL       |inc_0x03d784_0x041118| + 0xb68
	POP      {r3, pc}
	ADD      r1, r0, #0
	PUSH     {r3, lr}
	LDR      r2, [r1]
	LDR      r0, [pc, #0x28]
	SUB      r2, #1
	LDR      r0, [r0, #8]
	STR      r2, [r1]
	LSL      r2, r2, #2
	ADD      r1, r2, r1
	LDR      r1, [r1, #4]
	LDR      r2, [pc, #0x38]
	LSL      r3, r1, #2
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r1, r1, r2
	LDRB     r2, [r0, #5]
	CMP      r2, #1
	BNE      |loc_080008D2|
	LDR      r2, [r0, #0xc]
	CMP      r2, r1
	BEQ      |loc_080008D6|
|loc_080008D2|
	BL       |inc_0x03d784_0x041118| + 0x198c
|loc_080008D6|
	POP      {r3, pc}
|loc_080008D8|
	DCW      0x4fbc
	DCW      0x0805,0x82ec,0x086b,0xbce8,0x0806,0x2a60,0x0300,0x8f5d
	DCW      0x0002,0x6eec,0x087b,0x92a8,0x0831,0x05c4,0x0000,0xb78c
|loc_080008FA|
	LSR      r3, r7, #0x20
	LDR      r0, [pc, #0x274]
	LDR      r1, [r0, #8]
	MOV      r0, #0
	STRB     r0, [r1, #5]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x25c]
	LDR      r0, [r0, #0x24]
	BL       |loc_080096AC|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x244]
	LDR      r0, [r0, #0x24]
	BL       |loc_08009692|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x224]
	LDR      r0, [r0, #0x24]
	BL       |loc_080096C4|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x200]
	LDR      r0, [r0, #0x24]
	BL       |loc_08009728|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x1e0]
	LDR      r0, [r0, #0x24]
	BL       |loc_080096EA|
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      sp, #0x10
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #0xc]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #4]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	STR      r0, [sp]
	LDR      r0, [pc, #0x198]
	LDR      r4, [r0, #0x24]
	MOV      r0, sp
	ADD      r4, #0x80
	LDR      r1, [r4, #0x28]
	MOV      r2, #1
	BL       |loc_08009930|
	MOV      r2, #1
	MOV      r0, sp
	LDR      r1, [r4, #0x30]
	BL       |loc_08009930|
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      sp, #0x10
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #0xc]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #4]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	STR      r0, [sp]
	LDR      r0, [pc, #0x140]
	LDR      r4, [r0, #0x24]
	MOV      r0, sp
	ADD      r4, #0x80
	LDR      r1, [r4, #0x28]
	MOV      r2, #0
	BL       |loc_08009930|
	MOV      r2, #0
	MOV      r0, sp
	LDR      r1, [r4, #0x30]
	BL       |loc_08009930|
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0x14
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #0x10]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #0xc]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	STR      r0, [sp, #4]
	LDR      r0, [pc, #0xe4]
	LDR      r0, [r0, #0x24]
	ADD      r0, #0x80
	LDR      r1, [r0, #0x2c]
	ADD      r0, sp, #4
	MOV      r2, #1
	BL       |loc_08009930|
	ADD      sp, #0x14
	POP      {pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0x14
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #0x10]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #0xc]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	STR      r0, [sp, #4]
	LDR      r0, [pc, #0x94]
	LDR      r0, [r0, #0x24]
	ADD      r0, #0x80
	LDR      r1, [r0, #0x2c]
	ADD      r0, sp, #4
	MOV      r2, #0
	BL       |loc_08009930|
	ADD      sp, #0x14
	POP      {pc}
	LDR      r0, [pc, #0x80]
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x14]
	BL       |loc_080046F4|
	POP      {r3, pc}
	LDR      r0, [pc, #0x74]
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x14]
	BL       |loc_08004764|
	POP      {r3, pc}
	LDR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x64]
	LDR      r2, [r0]
	LDR      r1, [r1, #0x14]
	ADD      r1, r1, r2
	LDRB     r1, [r1, #2]
	STR      r1, [r0]
	BX       lr
|sub_08000B1C|
|unk_08000B1C|
	INCBIN	baserom.gba_0xb1c_0xb40.extracted
