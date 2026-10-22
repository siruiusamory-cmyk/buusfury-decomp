	CODE16
|sub_08006FFA|
	LSR      r4, r0, #0x20
	ADR      r4, |loc_080072E0|
	LSR      r4, r0, #0x20
	ADR      r0, |loc_08007054|
	LSR      r4, r0, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r4, sp, #0x220
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x60]
	ADD      r4, r0, #0
	LDR      r0, [r5, #8]
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r5, #4]
	BL       |loc_080115B0|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x20]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	ADD      r4, r0, #0
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
|unk_08007052|
	INCBIN	baserom.gba_0x7052_0x7054.extracted
|loc_08007054|
|unk_08007054|
	INCBIN	baserom.gba_0x7054_0x7056.extracted
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r4, pc}
