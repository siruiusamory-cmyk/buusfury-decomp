	CODE16
|__vecmap1c__FPvT1iPFPv_v|
	PUSH     {r6, r7, lr}
	PUSH     {r3, r4, r5}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	CMP      r0, r1
	BEQ      |loc_08047010|
|loc_08047004|
	ADD      r0, r4, #0
	BL       |sub_08046AAE|
	ADD      r4, r4, r6
	CMP      r4, r5
	BNE      |loc_08047004|
|loc_08047010|
	POP      {r3, r4, r5, r6, r7}
	POP      {r3}
	BX       r3
	LSL      r0, r0, #0
	PUSH     {r6, r7, lr}
	PUSH     {r3, r4, r5}
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r7, r2, #0
	ADD      r6, r3, #0
	CMP      r1, r2
	BCS      |loc_0804703A|
|loc_08047028|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x18]
	BL       |Thunk_JumpRegister1|
	ADD      r4, r4, r6
	ADD      r5, r5, r6
	CMP      r4, r7
	BCC      |loc_08047028|
|loc_0804703A|
	POP      {r3, r4, r5, r6, r7}
	POP      {r3}
	BX       r3
|sub_08047040|
|unk_08047040|
; cited by 0x08046E0A (a pc-relative load targets 0x0804708C)
	INCBIN	baserom.gba_0x47040_0x47648.extracted
	CODE16
|dat_08047648|
	DCW      0x0000
	DCW      0x7ff0
	DCW      0x2d18
	DCW      0x5444
	DCW      0x21fb
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

