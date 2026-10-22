	CODE16
|sub_0800A85E|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_0800A4A4|
	POP      {r4, pc}
|sub_0800A87A|
|unk_0800A87A|
; cited by 0x0800A7C8 (a pc-relative load targets 0x0800A87C)
	DCB	0x00,0x00
	DCD	0x0804D4E4
	DCD	0x0804BF80
	DCD	0x0804B318
		LDR r2, [pc, #0xa8]
		PUSH {r4, r5}
		LDR r2, [r2]
		CMP r2, #0
		BEQ      |inc_0x0158_0x143f2| + 0xa784
		ADD r3, r2, #0
		ADD r5, r1, #0
		ADD r5, #0xff
		ADD r3, #0xff
		ADD r3, #0x81
		ADD r5, #0x81
		LDR r4, [r5, #0x20]
		LDR r2, [r3, #0x20]
		LDR r3, [r3, #0x24]
		SUB r2, r2, r4
		LDR r4, [r5, #0x24]
		SUB r3, r3, r4
		ADD r4, r2, #0
		CMP r2, #0
		BGE      |loc_0800A8B2|
		NEG r4, r2
|loc_0800A8B2|
		ADD r5, r3, #0
		CMP r3, #0
		BGE      |loc_0800A8BA|
		NEG r5, r3
|loc_0800A8BA|
		CMP r4, r5
		BLT      |loc_0800A8CE|
		CMP r2, #0
		BLE      |loc_0800A8C8|
		MOV r2, #3
		STRB r2, [r1, #0x10]
		B        |inc_0x0158_0x143f2| + 0xa784
|loc_0800A8C8|
		MOV r2, #2
		STRB r2, [r1, #0x10]
		B        |inc_0x0158_0x143f2| + 0xa784
|loc_0800A8CE|
		CMP r3, #0
		BLE      |sub_0800A8D8|
		MOV r2, #0
		STRB r2, [r1, #0x10]
		B        |inc_0x0158_0x143f2| + 0xa784
