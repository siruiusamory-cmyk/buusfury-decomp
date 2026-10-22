	CODE16
|sub_080489A2|
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x210
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #8]
	MOV      r0, #2
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_080489B4|
	DCW      0x3118
	DCW      0x0300,0xb840
|loc_080489BA|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BLS      |loc_08048A58|
	LSR      r4, r0, #0x20
	ADD      r1, #0x20
	LSL      r0, r0, #0xc
	STMIA    r6!, {r5}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r3!, {r2, r3, r5, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r1, #0x28
	LSL      r0, r0, #0xc
	SUB      sp, #0x80
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048A02|
|unk_08048A02|
	INCBIN	baserom.gba_0x48a02_0x48a06.extracted
