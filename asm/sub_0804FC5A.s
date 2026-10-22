	CODE16
|sub_0804FC5A|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	LDRH     r0, [r1, #0x12]
	SUB      r0, #8
	STRH     r0, [r1, #0x12]
	BX       lr
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
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
	BL       |inc_0x0158_0x143f2| + 0xdd3c
	MOV      r0, #0x37
	STRB     r0, [r4, #8]
	POP      {r4, pc}
|sub_0804FCB6|
|unk_0804FCB6|
	INCBIN  baserom.gba_0x4fcb6_0x4fcb8.extracted
		BX       lr
	INCBIN  baserom.gba_0x4fcba_0x4fcbc.extracted
		BX       lr
	INCBIN  baserom.gba_0x4fcbe_0x4fcc0.extracted
		BX       lr
	INCBIN  baserom.gba_0x4fcc2_0x4fcc4.extracted
		BX       lr
	INCBIN  baserom.gba_0x4fcc6_0x4fcc8.extracted
		BX       lr
