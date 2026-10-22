	CODE16
|sub_08048642|
	LSL      r0, r0, #0xc
	LDR      r6, [sp, #0xc0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048650|
|unk_08048650|
	INCBIN	baserom.gba_0x48650_0x48652.extracted
