	CODE16
|sub_0804EA0A|
	LSR      r4, r0, #0x20
	LDR      r0, [r0, #4]
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0x24]
	BX       lr
	LSL      r0, r0, #0
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r1, [r0, #4]
	BX       lr
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r2, [r0]
	LDR      r3, [r2]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
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
	ADD      r2, #0x2c
	LSL      r0, r0, #0xc
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r1, #0xff
	ADD      r1, #0xc1
	MOV      r0, #0
	STR      r0, [r1, #0xc]
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r6, r4
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
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r1, #0xff
	ADD      r1, #0xc1
	MOV      r0, #0
	STR      r0, [r1, #0xc]
	MOV      r1, #0x11
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r7, r4
	LSL      r0, r0, #0xc
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	MOV      r3, #0
	STRH     r3, [r1, #0x12]
	MOV      r2, #0x38
	STRB     r2, [r1, #8]
	ADD      r1, #0xff
	ADD      r1, #0xa1
	ADD      r0, #4
	LDMIA    r0!, {r2}
	STMIA    r1!, {r2}
	LDR      r0, [r0]
	STR      r0, [r1]
	LDR      r0, [pc, #4]
	STR      r3, [r0]
	BX       lr
|sub_0804EAF0|
|unk_0804EAF0|
	INCBIN	baserom.gba_0x4eaf0_0x4eaf2.extracted
