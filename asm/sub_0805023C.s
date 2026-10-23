	CODE16
|sub_0805023C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r2, #0x56
	BL       |inc_0x046118_0x049114| + 0xcb8
	MOV      r1, #0x56
	LDRB     r1, [r1, r5]
	MOV      r0, #0x56
	ADD      r3, r5, #0
	STRB     r1, [r0, r4]
	MOV      r1, #0x57
	LDRB     r1, [r1, r5]
	MOV      r0, #0x57
	ADD      r3, #0x40
	STRB     r1, [r0, r4]
	MOV      r1, #0x58
	LDRH     r1, [r1, r5]
	MOV      r0, #0x58
	STRH     r1, [r0, r4]
	MOV      r1, #0x5a
	LDRH     r1, [r1, r5]
	MOV      r0, #0x5a
	STRH     r1, [r0, r4]
	MOV      r1, #0x5c
	LDRH     r1, [r1, r5]
	MOV      r0, #0x5c
	STRH     r1, [r0, r4]
	MOV      r1, #0x5e
	LDRH     r1, [r1, r5]
	MOV      r0, #0x5e
	STRH     r1, [r0, r4]
	MOV      r1, #0x60
	LDRH     r1, [r1, r5]
	MOV      r0, #0x60
	STRH     r1, [r0, r4]
	MOV      r1, #0x62
	LDRH     r1, [r1, r5]
	MOV      r0, #0x62
	STRH     r1, [r0, r4]
	MOV      r1, #0x64
	LDRH     r1, [r1, r5]
	MOV      r0, #0x64
	STRH     r1, [r0, r4]
	LDRH     r0, [r3, #0x26]
	ADD      r3, r4, #0
	ADD      r3, #0x40
	STRH     r0, [r3, #0x26]
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
	LDMIA    r1!, {r2}
	STR      r2, [r0]
	LDR      r1, [r1]
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	LDR      r2, [r1]
	STR      r2, [r0]
	LDR      r3, [r1, #4]
	STR      r3, [r0, #4]
	LDR      r1, [r1, #8]
	STR      r1, [r0, #8]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, lr}
	MOV      r6, #0x9f
	LSL      r6, r6, #3
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r2, r6, #0
	SUB      sp, #8
	BL       |inc_0x046118_0x049114| + 0xcb8
	LDR      r2, [pc, #0x28]
	MOV      r0, #0x45
	LSL      r0, r0, #5
	STR      r2, [sp]
	ADD      r2, r4, r0
	MOV      r3, #0x68
	ADD      r1, r4, r6
	ADD      r0, r5, r6
	BL       |inc_0x046118_0x049114| + 0xf00
	MOV      r1, #0x11
	LSL      r1, r1, #7
	ADD      r0, r5, r1
	ADD      r1, r4, r1
	LDR      r2, [r1, #0x20]
	LDR      r1, [r1, #0x24]
	STR      r1, [r0, #0x24]
	STR      r2, [r0, #0x20]
	ADD      sp, #8
	ADD      r0, r5, #0
	POP      {r4, r5, r6, pc}
|sub_080502F8|
|unk_080502F8|
	INCBIN	baserom.gba_0x502f8_0x502fa.extracted
|sub_080502FA|
	DCW      0x0805
