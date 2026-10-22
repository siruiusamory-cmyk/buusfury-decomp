	CODE16
|loc_08008192|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r2, [r1]
	SUB      sp, #0x50
	ASR      r2, r2, #0xa
	LSR      r3, r2, #8
	LDR      r2, [r1, #4]
	LDR      r4, [r1, #0x18]
	LSL      r3, r3, #8
	SUB      r4, r4, r3
	ASR      r4, r4, #4
	STR      r4, [sp, #0x18]
	ASR      r2, r2, #0xa
	LSR      r2, r2, #8
	LDR      r4, [r1, #0x1c]
	LSL      r2, r2, #8
	SUB      r4, r4, r2
	ASR      r4, r4, #3
	STR      r4, [sp, #0x1c]
	LDR      r4, [r1, #0x20]
	SUB      r4, r4, r3
	ADD      r4, #0xf
	ASR      r4, r4, #4
	STR      r4, [sp, #0x20]
	LDR      r1, [r1, #0x24]
	SUB      r1, r1, r2
	ADD      r1, #7
	ASR      r1, r1, #3
	STR      r1, [sp, #0x24]
	LSL      r1, r3, #0x17
	LSR      r4, r1, #0x1f
	LSL      r1, r2, #0x17
	LSR      r5, r1, #0x1f
	MOV      r1, #0
	STR      r1, [sp, #0x10]
	LDR      r1, [sp, #0x18]
	ADD      r2, sp, #0x18
	CMP      r1, #0
	BLE      |sub_080081E2|
	ADD      r1, r2, #0
	B        |Dma_Start3First|
