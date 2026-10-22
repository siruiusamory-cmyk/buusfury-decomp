	CODE16
|sub_08048B46|
	LSL      r0, r0, #0xc
	BVS      |loc_08048A84|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BLS      |loc_08048C30|
	LSR      r4, r0, #0x20
	ADD      r2, #0x2c
	LSL      r0, r0, #0xc
	POP      {r3, r6, pc}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048B76|
|unk_08048B76|
	INCBIN	baserom.gba_0x48b76_0x48b7a.extracted
