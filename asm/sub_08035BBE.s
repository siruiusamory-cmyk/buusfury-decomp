	CODE16
|sub_08035BBE|
	MOV      r1, #0x85
	LSL      r1, r1, #2
	ADD      r1, r5, r1
	LDR      r0, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0x12430
	POP      {r3, r4, r5, r6, r7, pc}
	ADR      r6, |loc_08035F30|
	LSR      r5, r6, #1
	LDR      r0, [pc, #0]
	BX       lr
|sub_08035BD4|
|unk_08035BD4|
	INCBIN	baserom.gba_0x35bd4_0x35bd6.extracted
