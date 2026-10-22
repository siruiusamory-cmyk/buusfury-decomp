	CODE16
|sub_0804840E|
	LSL      r0, r0, #0xc
	ADR      r2, |loc_08048464|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
	STR      r0, [r1]
	BX       lr
|sub_0804841C|
|unk_0804841C|
	INCBIN	baserom.gba_0x4841c_0x4841e.extracted
