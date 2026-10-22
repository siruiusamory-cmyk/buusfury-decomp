	CODE16
|sub_08039BCE|
	LSR      r7, r6, #1
	BLS      |loc_08039B74|
	LSR      r7, r5, #1
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	BCC      |sub_08039B6C|
	LSR      r4, r0, #0x20
	POP      {r3, r4, r6, pc}
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |sub_08039BF8|
	MOV      r0, #1
	POP      {r3, pc}
