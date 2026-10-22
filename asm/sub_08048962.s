	CODE16
|sub_08048962|
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x170]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #8]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048974|
|unk_08048974|
	INCBIN	baserom.gba_0x48974_0x48976.extracted
