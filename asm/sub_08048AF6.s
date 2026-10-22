	CODE16
|sub_08048AF6|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r4, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	LDR      r0, [pc, #0x14]
	STR      r0, [r1]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r2, #0x14
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r2, r5, r7}
	LSR      r4, r0, #0x20
|unk_08048B18|
	INCBIN	baserom.gba_0x48b18_0x48b1a.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048B24|
|unk_08048B24|
	INCBIN	baserom.gba_0x48b24_0x48b26.extracted
