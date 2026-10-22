	CODE16
|sub_08024630|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	SUB      r0, r2, #3
	CMP      r0, #5
	BCS      |loc_08024664|
	ADD      r3, pc, #0x8
	LDRB     r3, [r3, r0]
	LSL      r3, r3, #1
	ADD      pc, r3
	LSL      r0, r0, #0
|loc_08024644|
	ASR      r0, r2, #0x20
	LSL      r1, r2, #0xc
	LSL      r3, r0, #0
	LDR      r0, [pc, #0x64]
	LDR      r0, [r0]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_08024664|
	LDR      r1, [pc, #0x48]
	MOV      r0, #1
	STR      r0, [r1]
|loc_08024664|
	POP      {r3, r4, r5, pc}
|sub_08024666|
|unk_08024666|
; cited by 0x08024586 (a pc-relative load targets 0x0802469C)
	INCBIN	baserom.gba_0x24666_0x246a2.extracted
