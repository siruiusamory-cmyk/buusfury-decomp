	CODE16
|loc_080067F4|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r6, r4, #4
	MOV      r5, #0
	CMP      r0, #0
	BLE      |loc_0800681A|
|loc_08006802|
	LSL      r0, r5, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #4]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_08006802|
|loc_0800681A|
	MOV      r0, #0xff
	ADD      r0, #9
	LDR      r0, [r0, r4]
	CMP      r0, #0
	BEQ      |loc_08006836|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0800685E|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_08006836|
	LDR      r0, [r4, #4]
	MOV      r5, #0
	CMP      r0, #0
	BLE      |loc_0800685E|
|loc_0800683E|
	LSL      r0, r5, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_08006856|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_08006856|
	LDR      r0, [r4, #4]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_0800683E|
|loc_0800685E|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r4, r5, r6, pc}
|sub_0800686C|
|unk_0800686C|
	INCBIN	baserom.gba_0x686c_0x686e.extracted
	CODE16
|dat_0800686E|
	DCW      0x0804
	DCW      0x91f0
	DCW      0x0804
	DCW      0x0158
	DCW      0x0807
	DCW      0xf5a5
	DCW      0x0803
	DCW      0xbce8
	DCW      0x0806

