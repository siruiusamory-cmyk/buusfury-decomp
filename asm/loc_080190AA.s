	CODE16
|loc_080190AA|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x184]
	ADD      r7, r1, #0
	STR      r0, [r5]
	LDR      r0, [r1, #0xc]
	MOV      r4, #0
	CMP      r0, #0
	STR      r0, [r5, #4]
	BLE      |loc_080190D8|
|loc_080190BE|
	LSL      r6, r4, #2
	ADD      r0, r6, r7
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	LDR      r1, [sp, #8]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r6, r5
	STR      r0, [r1, #8]
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_080190BE|
|loc_080190D8|
	ADD      r0, r5, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	ADD      r6, r1, #0
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08019106|
|loc_080190EC|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r6, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_080190EC|
|loc_08019106|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [r0, #4]
	ADD      r7, r1, #0
	MOV      r5, #1
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08019134|
|loc_08019118|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r7, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	AND      r5, r0
	LDR      r0, [r6, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08019118|
|loc_08019134|
	ADD      r0, r5, #0
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	ADD      r6, r1, #0
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08019160|
|loc_08019146|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r6, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08019146|
|loc_08019160|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [r0, #4]
	ADD      r7, r1, #0
	MOV      r5, #0
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_0801918E|
|loc_08019172|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r7, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ORR      r5, r0
	LDR      r0, [r6, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08019172|
|loc_0801918E|
	ADD      r0, r5, #0
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	ADD      r6, r1, #0
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_080191C2|
|loc_080191A0|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r6, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_080191BA|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|loc_080191BA|
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_080191A0|
|loc_080191C2|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r6, r1, #0
	LSL      r0, r0, #2
	ADD      r0, #0xc
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_080191E4|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_080190AA|
|loc_080191E4|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r6, r1, #0
	LSL      r0, r0, #2
	ADD      r0, #0xc
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0801920A|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_080190AA|
	LDR      r0, [pc, #0x30]
	STR      r0, [r4]
|loc_0801920A|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r6, r1, #0
	LSL      r0, r0, #2
	ADD      r0, #0xc
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_08019230|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_080190AA|
	LDR      r0, [pc, #0xc]
	STR      r0, [r4]
|loc_08019230|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08019234|
	DCW      0xbda8
	DCW      0x0804,0xb6d0
|loc_0801923A|
	LSR      r4, r0, #0x20
	ADD      r7, pc, #0x40
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_08019264|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08019264|
	MOV      r0, #1
	POP      {r4, pc}
|sub_08019268|
|unk_08019268|
	INCBIN	baserom.gba_0x19268_0x1926c.extracted
