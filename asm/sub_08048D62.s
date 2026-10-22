	CODE16
|sub_08048D62|
	LSL      r0, r0, #0xc
	STMIA    r3!, {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D70|
|unk_08048D70|
	INCBIN	baserom.gba_0x48d70_0x48d72.extracted
