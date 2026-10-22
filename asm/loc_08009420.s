	CODE16
|loc_08009420|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x228]
	ADD      r4, r1, #0
	LDR      r0, [r7, #0xc]
	BL       |loc_08011B04|
	LDR      r0, [r4, #0x24]
	CMP      r0, #0
	BEQ      |loc_08009476|
	LDR      r0, [r4, #0x3c]
	CMP      r0, #0
	BEQ      |sub_08009478|
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_0800CE1A|
	ADD      r6, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [r7, #0xc]
	BL       |List_Append|
	LDR      r0, [r4, #0x24]
	MOV      r5, #1
	CMP      r0, #1
	BLE      |loc_08009476|
|loc_08009452|
	LSL      r1, r5, #1
	ADD      r1, r1, r5
	LDR      r0, [r4, #0x28]
	LSL      r1, r1, #3
	ADD      r1, r0, r1
	ADD      r3, r5, #0
	ADD      r2, r6, #0
	MOV      r0, #0
	BL       |loc_0800CD78|
	ADD      r1, r0, #0
	LDR      r0, [r7, #0xc]
	BL       |List_Append|
	LDR      r0, [r4, #0x24]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_08009452|
|loc_08009476|
	POP      {r3, r4, r5, r6, r7, pc}
