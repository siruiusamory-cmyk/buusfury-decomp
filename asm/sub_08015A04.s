	CODE16
|sub_08015A04|
	LDR      r1, [pc, #0x1c]
	PUSH     {r4, lr}
	LDR      r4, [r1]
	LDR      r0, [r0, #8]
	LDR      r1, [pc, #0x18]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LDR      r0, [pc, #0x14]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, r0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, pc}
|sub_08015A24|
|unk_08015A24|
	INCBIN	baserom.gba_0x15a24_0x15a26.extracted
