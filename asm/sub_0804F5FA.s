	CODE16
|sub_0804F5FA|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	BL       |inc_0x0158_0x143f2| + 0xf7fc
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r0, #0
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0xc]
	BX       lr
	LSL      r0, r0, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	ADD      r0, #4
	LDMIA    r0!, {r2}
	STMIA    r1!, {r2}
	LDR      r0, [r0]
	STR      r0, [r1]
	BX       lr
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	MOV      r0, #1
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0xc]
	BX       lr
	LSL      r0, r0, #0
	MOV      r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x61
	STRH     r0, [r1, #0x16]
	BX       lr
	LSL      r0, r0, #0
	MOV      r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x61
	STRH     r0, [r1, #0x16]
	BX       lr
|sub_0804F672|
|unk_0804F672|
	INCBIN  baserom.gba_0x4f672_0x4f674.extracted
		BX       lr
