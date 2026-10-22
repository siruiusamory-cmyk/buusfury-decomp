	CODE16
|sub_08048806|
	LSL      r0, r0, #0xc
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
