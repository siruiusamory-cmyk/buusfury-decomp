	CODE16
|sub_080485DE|
	LSL      r0, r0, #0xc
	LDR      r1, [sp, #0x3f0]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r5, sp, #0x3c0
	LSR      r4, r0, #0x20
	CMP      r7, #0xc4
	LSL      r0, r0, #0xc
	LDR      r4, [sp, #0x60]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #8
	STR      r0, [r1]
|loc_0804860C|
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r4!, {r4}
	LSR      r4, r0, #0x20
	CMP      r7, #0xcc
	LSL      r0, r0, #0xc
|unk_08048618|
	INCBIN	baserom.gba_0x48618_0x4861a.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_08048620|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_0804862A|
|unk_0804862A|
	INCBIN	baserom.gba_0x4862a_0x4862e.extracted
