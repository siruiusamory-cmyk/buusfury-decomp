	CODE16
|sub_08047648|
	LSL      r0, r0, #0
	LDRB     r0, [r6, #0x1f]
	CMP      r5, #0x18
	STRB     r4, [r0, r1]
	MOV      r1, #0xfb
|unk_08047652|
	INCBIN	baserom.gba_0x47652_0x47654.extracted
	CMP      r5, #0x18
	STRB     r4, [r0, r1]
	MOV      r1, #0xfb
	SUB      r7, #0xf9
	CMP      r5, #0x18
	STRB     r4, [r0, r1]
	MOV      r1, #0xfb
	STMIA    r0!, {r0, r3}
	CMP      r5, #0x18
	STRB     r4, [r0, r1]
	MOV      r1, #0xfb
	AND      r1, r1
	LSL      r1, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LDRB     r0, [r7, #0x1f]
	LSL      r4, r0, #0xb
	LSL      r7, r6, #1
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LDRB     r7, [r0, r0]
	ADD      r3, #0x14
|unk_08047684|
	INCBIN	baserom.gba_0x47684_0x47686.extracted
	SUB      r4, #0xa1
	PUSH     {r3, lr}
	BL       |loc_08047FC0|
	LDR      r0, [r0]
	ADD      sp, #4
	POP      {r3}
	BX       r3
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_08047FC0|
	STR      r4, [r0]
	POP      {r4}
	POP      {r3}
	BX       r3
|sub_080476A6|
|unk_080476A6|
	INCBIN	baserom.gba_0x476a6_0x476a8.extracted
