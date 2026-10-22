	CODE16
|sub_080502FA|
	LSR      r5, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_08050316|
	MOV      r0, #0xff
	ADD      r0, #0x2d
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08050316|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08050316|
	LDR      r0, [pc, #0x3c]
	MOV      r6, #0
	STR      r0, [r4]
	MOV      r0, #0xff
	ADD      r0, #0x15
	STRB     r5, [r0, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	STR      r6, [r5, #0x1c]
	STR      r6, [r5, #0x20]
	ADD      r0, r4, #0
	MVN      r1, r6
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |sub_0804912C|
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |sub_0804912C|
	LDR      r0, [pc, #0x10]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x10]
	STR      r6, [r0]
	LDR      r0, [pc, #0x10]
	STR      r6, [r0]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08050354|
	DCW      0x92ec
	DCW      0x0804,0xffff
|loc_0805035A|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BNE      |loc_08050378|
	MOV      r0, #0x68
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08050378|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_08050378|
	ADD      r1, r4, #0
	ADD      r1, #0x3a
	MOV      r2, #2
	ADD      r0, r4, #0
	ADD      r0, #0x2e
	LDR      r3, [pc, #0x18]
	BL       |inc_0x046118_0x049114| + 0xedc
	ADD      r1, r4, #0
	ADD      r1, #0x4c
	MOV      r2, #4
	ADD      r0, r4, #0
	ADD      r0, #0x3c
	LDR      r3, [pc, #0xc]
	BL       |inc_0x046118_0x049114| + 0xedc
	ADD      r0, r4, #0
	POP      {r4, pc}
|sub_0805039C|
|unk_0805039C|
	INCBIN	baserom.gba_0x5039c_0x5039e.extracted
