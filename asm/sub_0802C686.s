	CODE16
|sub_0802C686|
	LSL      r0, r0, #0xc
	ADD      r0, #0x94
	LSL      r0, r0, #0xc
	BL       |loc_0802d674| + 0x1a
	SUB      r0, r0, r4
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #0x150]
	LSR      r5, r6, #1
|unk_0802C698|
	INCBIN	baserom.gba_0x2c698_0x2c69a.extracted
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	BNE      |sub_0802C6B0|
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802C6B0|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
