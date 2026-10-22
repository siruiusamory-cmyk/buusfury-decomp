	CODE16
|sub_08048C86|
	LSL      r0, r0, #0xc
|loc_08048C88|
	STMIA    r1!, {r2, r4, r5, r7}
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
	ADD      r2, #0x8c
	LSL      r0, r0, #0xc
|loc_08048CA4|
	STMIA    r7!, {r2, r4, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r5, sp, #0x220
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #8
	STR      r0, [r1]
	BX       lr
|loc_08048CBA|
	DCW      0x0000
	DCW      0xcff0,0x0804,0x3294,0x0300,0xb630
|loc_08048CC6|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_08048CD6|
	DCW      0x0000
	DCW      0xd014,0x0804,0x32a0,0x0300,0xb668
|loc_08048CE2|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048CEC|
	DCW      0x32a8
	DCW      0x0300,0xb688
|loc_08048CF2|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048CFC|
	DCW      0x32ac
	DCW      0x0300,0xcb00
|loc_08048D02|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D0C|
|unk_08048D0C|
	INCBIN	baserom.gba_0x48d0c_0x48d0e.extracted
