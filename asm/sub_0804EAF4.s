	CODE16
|sub_0804EAF4|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x15
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r1, #0x20
	LSL      r0, r0, #0xc
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r7, r4
	LSL      r0, r0, #0xc
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r6, r4
	LSL      r0, r0, #0xc
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r1, [r0, #4]
	BX       lr
	ADD      r2, r0, #0
	PUSH     {r3, lr}
	MOV      r3, #0
	ADD      r2, #4
	STR      r3, [r2]
	STR      r3, [r2, #4]
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x14
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r6, r4
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	BL       |inc_0x0158_0x143f2| + 0xdd08
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r2, [r0]
	LDR      r3, [r2]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x15
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r1, #0x30
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r6, r4
	LSL      r0, r0, #0xc
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	BL       |inc_0x0158_0x143f2| + 0xdd08
	MOV      r0, #0x37
	STRB     r0, [r4, #8]
	POP      {r4, pc}
	LSL      r0, r0, #0
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
|sub_0804EC02|
|unk_0804EC02|
	INCBIN  baserom.gba_0x4ec02_0x4ec04.extracted
		BX       lr
	INCBIN  baserom.gba_0x4ec06_0x4ec08.extracted
		BX       lr
|sub_0804EC0A|
	DCW      0x0000
