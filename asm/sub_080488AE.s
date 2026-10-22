	CODE16
|sub_080488AE|
	LSL      r0, r0, #0xc
	ADR      r6, |sub_08048AF4|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_080488B8|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BCC      |loc_08048930|
	LSR      r4, r0, #0x20
	ADD      r0, #0xc8
	LSL      r0, r0, #0xc
	POP      {r4, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r2!, {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r0, #0xd0
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x1d0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080488F4|
|unk_080488F4|
	INCBIN	baserom.gba_0x488f4_0x488f6.extracted
