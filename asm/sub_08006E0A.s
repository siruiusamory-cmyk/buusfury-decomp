	CODE16
|sub_08006E0A|
	PUSH     {r3, lr}
	BL       |loc_08007064|
	POP      {r3, pc}
	LSL      r0, r0, #0
	STR      r6, [sp, #0x330]
	LSR      r4, r0, #0x20
|unk_08006E18|
	INCBIN	baserom.gba_0x6e18_0x6e1a.extracted
	LSR      r4, r0, #0x20
	STR      r5, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	PUSH     {r2, r3, r4, r5, r6, lr}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0xc]
	LDR      r0, [r0]
	BL       |loc_08011AA0|
	LDR      r0, [r4, #4]
	BL       |loc_080124F8|
	POP      {r4, pc}
|sub_08006E38|
|unk_08006E38|
	INCBIN	baserom.gba_0x6e38_0x6e3a.extracted
