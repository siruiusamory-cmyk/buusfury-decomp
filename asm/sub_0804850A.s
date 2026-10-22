	CODE16
|sub_0804850A|
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x130]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048518|
|unk_08048518|
	INCBIN	baserom.gba_0x48518_0x4851a.extracted
