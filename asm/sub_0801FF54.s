	CODE16
|sub_0801FF54|
	EXPORT |sub_0801FF54|
	PUSH     {r2, r3, r5, r7, lr}
	LSR      r4, r0, #0x20
	LDR      r3, [sp, #0xb0]
	LSR      r4, r0, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSR      r4, r7, #0x20
	LSR      r2, r6, #1
	STR      r4, [sp, #0x1f0]
	LSR      r1, r6, #0x20
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	ADD      r0, #0xff
	ADD      r0, #1
	CMP      r2, #0
	BEQ      |loc_0801FF7C|
	CMP      r2, #1
	BEQ      |loc_0801FF7C|
	CMP      r2, #2
	BNE      |loc_0801FF8E|
|loc_0801FF7C|
	LDR      r1, [r0, #0x2c]
	ADD      r1, #1
	STR      r1, [r0, #0x2c]
	CMP      r1, #0x14
	BLE      |loc_0801FF8C|
	LDR      r1, [pc, #0xc]
	MOV      r0, #1
	STR      r0, [r1]
|loc_0801FF8C|
	BX       lr
|loc_0801FF8E|
	MOV      r1, #0
	STR      r1, [r0, #0x2c]
	BX       lr
|sub_0801FF94|
|unk_0801FF94|
	INCBIN	baserom.gba_0x1ff94_0x1ff96.extracted
|sub_0801FF96|
	DCW      0x0300
