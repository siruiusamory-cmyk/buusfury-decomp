	CODE16
|sub_080484E6|
	LSL      r0, r0, #0xc
	STR      r7, [sp, #0x290]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #8]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080484F8|
|unk_080484F8|
	INCBIN	baserom.gba_0x484f8_0x484fa.extracted
