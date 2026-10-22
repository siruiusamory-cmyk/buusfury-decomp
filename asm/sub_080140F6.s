	CODE16
|sub_080140F6|
	MOV      r2, #0
	STR      r2, [sp]
	ADD      r2, r0, #0
	ADD      r1, r0, #0
	ADD      r1, #0x24
	ADD      r2, #0x34
	LDR      r3, [r0, #0x20]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x7c6
	ADD      sp, #8
	POP      {r4, pc}
	LSL      r0, r0, #0
	LDR      r0, [sp, #0x200]
	LSR      r4, r0, #0x20
	STRB     r4, [r4, #0x1e]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x270]
	LSR      r4, r0, #0x20
|unk_0801411C|
	INCBIN	baserom.gba_0x1411c_0x1411e.extracted
	LSR      r4, r0, #0x20
	MOV      r0, #0
	BX       lr
