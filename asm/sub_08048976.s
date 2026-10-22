	CODE16
|sub_08048976|
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #8
	STR      r0, [r1]
	BX       lr
|sub_0804898A|
|unk_0804898A|
	INCBIN	baserom.gba_0x4898a_0x4898e.extracted
