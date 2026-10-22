	CODE16
|sub_080505AE|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BNE      |loc_080505C6|
	MOV      r0, #0xff
	ADD      r0, #0x31
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080505C6|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_080505C6|
	LDR      r0, [pc, #0x44]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #5
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #6
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |sub_0804912C|
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |sub_0804912C|
	LDR      r0, [pc, #0x18]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r0, [r4]
	STR      r6, [r5, #0x2c]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0805060C|
	DCW      0x92ec
	DCW      0x0804,0xffff
|loc_08050612|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	ADD      sp, #0x140
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BNE      |loc_08050636|
	MOV      r0, #0xff
	ADD      r0, #0x2d
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08050636|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08050636|
	LDR      r0, [pc, #0x44]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #6
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #7
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |sub_0804912C|
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |sub_0804912C|
	LDR      r0, [pc, #0x18]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r0, [r4]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0805067A|
	DCW      0x0000
	DCW      0x92ec,0x0804,0xffff
|loc_08050682|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
|unk_0805068C|
	INCBIN	baserom.gba_0x5068c_0x5068e.extracted
	LSR      r4, r0, #0x20
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_080506AC|
	MOV      r0, #0x2c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080506AC|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
