	CODE16
|sub_0800399E|
	MOV      r2, #0
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	SUB      r1, #4
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	ADD      r1, sp, #4
	SUB      r0, #4
	STR      r0, [sp, #4]
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xa9f2
	ADD      r1, r0, #0
	LDR      r0, [pc, #8]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	ADD      sp, #0xc
	POP      {pc}
|sub_080039D4|
|unk_080039D4|
	INCBIN	baserom.gba_0x39d4_0x39d6.extracted
