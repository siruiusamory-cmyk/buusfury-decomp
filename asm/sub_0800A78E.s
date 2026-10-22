	CODE16
|sub_0800A78E|
	LSR      r7, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	BMI      |loc_0800A760|
	LSR      r4, r0, #0x20
	BEQ      |loc_0800A72C|
	LSR      r4, r0, #0x20
|unk_0800A79C|
	INCBIN	baserom.gba_0xa79c_0xa79e.extracted
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800A7C0|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
