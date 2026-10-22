	CODE16
|sub_08048846|
	LSL      r0, r0, #0xc
|unk_08048848|
	INCBIN	baserom.gba_0x48848_0x4884a.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r4!, {r2, r4, r5, r6, r7}
	LSR      r4, r0, #0x20
|loc_08048860|
	ADD      r0, #0xa8
	LSL      r0, r0, #0xc
|unk_08048864|
	INCBIN	baserom.gba_0x48864_0x48866.extracted
	LSR      r4, r0, #0x20
