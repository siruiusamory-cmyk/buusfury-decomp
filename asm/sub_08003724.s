	CODE16
|sub_08003724|
	PUSH     {r3, lr}
	MOV      r1, #1
	MOV      r0, #0
	BL       |inc_0x331c0_0x341c0| + 0x3fc
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, pc}
	LDR      r1, [pc, #0x29c]
	LDR      r1, [r1]
	LDRH     r1, [r1, #4]
	LSL      r2, r1, #0x1f
	LDR      r1, [r0]
	LSR      r2, r2, #0x1f
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r3, lr}
	BL       |inc_0x03d784_0x041118| + 0x22b4
	POP      {r3, pc}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x270]
	CMP      r0, #0
	LDR      r1, [r1, #0xc]
	BEQ      |loc_0800376E|
	MOV      r0, #1
	STR      r0, [r1, #0xc]
	BX       lr
|loc_0800376E|
	MOV      r0, #0
	STR      r0, [r1, #0xc]
	BX       lr
	PUSH     {r4, r5, r6}
	MOV      r5, #0x9f
	LDR      r6, [pc, #0x258]
	MOV      r2, #0
	MOV      r1, #0
	LSL      r5, r5, #3
|loc_08003780|
	MOV      r3, #0x68
	LDR      r4, [r6, #0x14]
	MUL      r3, r1
	ADD      r3, r3, r4
	ADD      r3, r3, r5
	ADD      r3, #0x24
	LDR      r3, [r3]
	ADD      r2, r3, r2
	ADD      r1, #1
	CMP      r1, #5
	BLT      |loc_08003780|
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r4, r5, r6}
	BX       lr
	LDR      r1, [r0]
	LDR      r3, [pc, #0x22c]
	SUB      r1, #1
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	STR      r1, [r0]
	LDR      r2, [r2, #4]
	LSL      r2, r2, #2
	LDR      r2, [r3, r2]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [r0]
	LDR      r3, [pc, #0x218]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r1, [pc, #0x208]
	MUL      r2, r3
	LDRH     r0, [r1, #0x10]
	ASR      r2, r2, #8
	ADD      r0, r0, r2
	STRH     r0, [r1, #0x10]
	BX       lr
	LDR      r1, [r0]
	MOV      r3, #0xa4
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r1, [pc, #0x1ec]
	MUL      r2, r3
	LDRH     r0, [r1, #8]
	ASR      r2, r2, #6
	ADD      r0, r0, r2
	STRH     r0, [r1, #8]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x1d4]
	LDR      r0, [r0, #4]
	LDR      r2, [r1, #0x20]
	ADD      r2, r2, r0
	STR      r2, [r1, #0x20]
	LDR      r2, [r1, #0x1c]
	ADD      r0, r2, r0
	STR      r0, [r1, #0x1c]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x1b8]
	LDR      r0, [r0, #4]
	LDR      r2, [r1, #0x18]
	ADD      r0, r0, r2
	STR      r0, [r1, #0x18]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x1a0]
	LDR      r0, [r0, #4]
	LDR      r2, [r1, #0x24]
	ADD      r0, r0, r2
	STR      r0, [r1, #0x24]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x18c]
	LDR      r0, [r0, #4]
	LDR      r2, [r1, #0x14]
	ADD      r0, r0, r2
	STR      r0, [r1, #0x14]
	BX       lr
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x17c]
	ADD      r4, #0xc
	LDRH     r1, [r4]
	MOV      r0, #2
	BL       |inc_0x046118_0x049114| + 0xd40
	STRH     r0, [r4]
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x16c]
	ADD      r4, #1
	LDRB     r1, [r4]
	MOV      r0, #2
	BL       |inc_0x046118_0x049114| + 0xd40
	STRB     r0, [r4]
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x158]
	ADD      r4, #2
	LDRB     r1, [r4]
	MOV      r0, #2
	BL       |inc_0x046118_0x049114| + 0xd40
	STRB     r0, [r4]
	POP      {r4, pc}
	LDR      r0, [pc, #0x148]
	LDRH     r1, [r0, #0xe]
	LSL      r3, r1, #3
	SUB      r1, r3, r1
	LSR      r1, r1, #3
	STRH     r1, [r0, #0xe]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x130]
	LDR      r0, [r0, #4]
	LDRB     r2, [r1]
	ADD      r0, r0, r2
	STRB     r0, [r1]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	MOV      r0, #0
	BL       |inc_0x351c0_0x3d4d0| + 0x127c
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x108]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	POP      {r3, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	ADD      r2, sp, #4
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	MOV      r1, #0x23
	STR      r0, [sp, #4]
	LDR      r0, [pc, #0xd8]
	LDR      r0, [r0, #0x18]
	BL       |loc_08011C0C|
	ADD      sp, #0xc
	POP      {pc}
	PUSH     {r4, lr}
	LDR      r3, [r0]
	SUB      r3, #1
	LSL      r1, r3, #2
	STR      r3, [r0]
	ADD      r1, r1, r0
	LDR      r2, [r1, #4]
	SUB      r3, #1
	LSL      r1, r3, #2
	STR      r3, [r0]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	SUB      r3, #1
	STR      r3, [r0]
	LSL      r3, r3, #2
	ADD      r0, r3, r0
	LDR      r4, [r0, #4]
	MOV      r3, #0x68
	LDR      r0, [pc, #0xa8]
	MUL      r3, r4
	LDR      r0, [r0, #0x14]
	ADD      r0, r3, r0
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r0, r0, r3
	BL       |loc_08013B54|
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	MOV      r3, #0x68
	SUB      r0, #1
	LSL      r1, r0, #2
	STR      r0, [r4]
	ADD      r1, r1, r4
	LDR      r1, [r1, #4]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r2, [r0, #4]
	LDR      r0, [pc, #0x78]
	MUL      r2, r3
	LDR      r0, [r0, #0x14]
	ADD      r0, r2, r0
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r0, r0, r2
	BL       |loc_08013BCC|
	LDR      r1, [r4]
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r1, r1, r4
	STR      r2, [r4]
	STR      r0, [r1, #4]
	POP      {r4, pc}
	LDR      r0, [pc, #0x58]
	MOV      r2, #0x40
	LDR      r0, [r0, #0x14]
	LDRB     r1, [r0, #1]
	ORR      r1, r2
	STRB     r1, [r0, #1]
	BX       lr
|sub_08003986|
|unk_08003986|
	INCBIN	baserom.gba_0x3986_0x399e.extracted
