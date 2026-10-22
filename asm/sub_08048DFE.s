	CODE16
|sub_08048DFE|
	LSL      r0, r0, #0xc
	BCS      |loc_08048DB4|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STR      r3, [sp, #0x320]
	LSR      r4, r0, #0x20
	ADD      r4, #0x8c
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x1b0]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [sp, #0xd0]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0x1c0]
	LSL      r0, r0, #0xc
|unk_08048E38|
	INCBIN	baserom.gba_0x48e38_0x48e3a.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #4]
	LDR      r1, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048E44|
|unk_08048E44|
	INCBIN	baserom.gba_0x48e44_0x48e46.extracted
