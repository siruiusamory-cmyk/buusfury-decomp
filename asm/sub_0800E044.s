	CODE16
|sub_0800E044|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [pc, #0x18]
	BL       |loc_0800ED18|
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|loc_0800E062|
	DCW      0x0000
	DCW      0x1b00,0x0300,0x25b8,0x0807,0x92a8,0x0831,0x05c4,0x0000
