	CODE16
|sub_08048D2E|
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r2, r4, r5}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #8]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D40|
|unk_08048D40|
	INCBIN	baserom.gba_0x48d40_0x48d42.extracted
