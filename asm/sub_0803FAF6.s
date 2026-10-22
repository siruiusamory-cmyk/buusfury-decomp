	CODE16
|sub_0803FAF6|
	PUSH     {r4, r5}
	MOV      r4, #1
	MOV      r2, #0
	MOV      r1, #0xf
	MOV      r5, #2
|loc_0803FB00|
	ADD      r3, r4, #0
	LSL      r3, r1
	ADD      r3, r3, r2
	LSL      r3, r1
	CMP      r3, r0
	BHI      |loc_0803FB14|
	SUB      r0, r0, r3
	ADD      r3, r5, #0
	LSL      r3, r1
	ORR      r2, r3
|loc_0803FB14|
	SUB      r1, #1
	BPL      |loc_0803FB00|
	LSR      r0, r2, #1
	POP      {r4, r5}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r7, r1, #0
	MOV      r5, #0
	MOV      r4, #0x1f
	SUB      sp, #0xc
|loc_0803FB2A|
	MOV      r0, #1
	LSL      r0, r4
	ADD      r0, r0, r5
	MOV      r1, #0
	STR      r1, [sp, #8]
	ADD      r2, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x046118_0x049114| + 0xae4
	ADD      r3, r1, #0
	ADD      r1, r7, #0
	ADD      r2, r0, #0
	ADD      r0, r6, #0
	BL       |inc_0x046118_0x049114| + 0xa10
	BCC      |loc_0803FB64|
	ADD      r1, sp, #4
	LDMIA    r1!, {r0, r1}
	ADD      r2, r4, #0
	BL       |inc_0x046118_0x049114| + 0xae4
	ADD      r3, r1, #0
	ADD      r1, r7, #0
	SUB      r6, r6, r0
	SBC      r1, r3
	ADD      r7, r1, #0
	MOV      r0, #2
	LSL      r0, r4
	ORR      r5, r0
|loc_0803FB64|
	SUB      r4, #1
	BPL      |loc_0803FB2A|
	LSR      r0, r5, #1
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|loc_0803FB6E|
	DCW      0x0000
	DCW      0x4a5c,0x0300,0xbc71,0x02cb,0xd80f,0x0632
