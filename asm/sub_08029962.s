	CODE16
|sub_08029962|
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STMIA    r3!, {r2, r4}
	LSR      r4, r0, #0x20
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	CMP      r7, #0xe8
	LSL      r0, r0, #0xc
	MOV      r0, #0x8b
	LSL      r0, r0, #2
	PUSH     {r3, lr}
	ADD      r0, r1, r0
	BL       |inc_0x0158_0x143f2| + 0xa802
	MOV      r0, #0
	POP      {r3, pc}
	MOV      r0, #0x8b
	LSL      r0, r0, #2
	ADD      r0, r1, r0
	PUSH     {r3, lr}
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_080299A0|
	LDR      r2, [r0]
	LDR      r3, [r2, #0xc]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080299A0|
	POP      {r3, pc}
|sub_080299A2|
|unk_080299A2|
	INCBIN	baserom.gba_0x299a2_0x299a6.extracted
|sub_080299A6|
	DCW      0x0000
	DCW      0x2fec
	DCW      0x0300
