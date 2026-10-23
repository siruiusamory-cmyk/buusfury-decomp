	CODE16
|sub_080487CA|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_080487D4|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r5!, {r3, r4}
	LSR      r4, r0, #0x20
	ADD      r0, #0x74
	LSL      r0, r0, #0xc
|unk_080487E8|
	INCBIN	baserom.gba_0x487e8_0x487ea.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080487F4|
|unk_080487F4|
	INCBIN	baserom.gba_0x487f4_0x487f6.extracted
	CODE16
|dat_080487F6|
	DCW      0x0300
|unk_080487F8|
	INCBIN	baserom.gba_0x487f8_0x487fa.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048804|
|unk_08048804|
	INCBIN	baserom.gba_0x48804_0x48806.extracted
	CODE16
|dat_08048806|
	DCW      0x0300
|unk_08048808|
	INCBIN	baserom.gba_0x48808_0x4880a.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, #0x8c
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r2, r3, r6, r7}
	LSR      r4, r0, #0x20
|unk_08048828|
	INCBIN	baserom.gba_0x48828_0x4882a.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048834|
	DCW      0x30a0
	DCW      0x0300,0xbd88
|loc_0804883A|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048844|
|unk_08048844|
	INCBIN	baserom.gba_0x48844_0x48846.extracted
	CODE16
|dat_08048846|
	DCW      0x0300
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

