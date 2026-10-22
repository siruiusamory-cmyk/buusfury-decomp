	CODE16
|sub_08048BF6|
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0x120
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BCC      |loc_08048C30|
	LSR      r4, r0, #0x20
	ADD      r2, #0x5c
	LSL      r0, r0, #0xc
	POP      {r3, r4, r5, r6}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r3!, {r3, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r2, #0x64
	LSL      r0, r0, #0xc
|loc_08048C30|
	SUB      sp, #0x40
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048C42|
|unk_08048C42|
	INCBIN	baserom.gba_0x48c42_0x48c46.extracted
