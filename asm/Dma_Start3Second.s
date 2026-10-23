|Dma_Start3Second|
	CODE16
|unk_08008306|
		B        |loc_08008364|
|loc_08008308|
|unk_08008308|
		MOV r6, #1
		EOR r6, r4
		LDR r2, [sp, #0x48]
		LSL r6, r6, #5
		ADD r2, r2, r6
		LDR r6, [pc, #0x194]
		ADD r7, r2, r6
		LDR r2, [sp, #0x20]
		LSL r6, r2, #1
		LDR r2, [sp, #0x1c]
		SUB r6, #0x20
		LSL r2, r2, #0x1b
		LSR r2, r2, #0x1b
		STR r6, [sp, #0xc]
		LSL r6, r2, #6
		MOV ip, r6
		ADD ip, r7
		LDR r6, [r0, #0x10]
		LSL r7, r2, #5
		MOV lr, r6
		ADD lr, r7
		CMP r2, #0x20
		BGE      |loc_08008364|
		LDR r6, [sp, #0xc]
		LDR r7, [pc, #0x170]
		LSL r6, r6, #0xf
		LSR r6, r6, #0x10
		STR r6, [sp, #0x40]
|loc_08008340|
		MOV r6, lr
		STR r6, [r7]
		MOV r6, ip
		STR r6, [r7, #4]
		LDR r6, [sp, #0x40]
		STRH r6, [r7, #8]
		MOV r6, #1
		LSL r6, r6, #0xf
		STRH r6, [r7, #0xa]
		MOV r6, lr
		ADD r6, #0x20
		MOV lr, r6
		MOV r6, ip
		ADD r6, #0x40
		ADD r2, #1
		CMP r2, #0x20
		MOV ip, r6
		BLT      |loc_08008340|
|loc_08008364|
		LDR r2, [sp, #0x18]
		CMP r2, #0
		BGE      |loc_080083CA|
		MOV r6, #1
		EOR r6, r4
		LSL r6, r6, #5
		LSL r2, r5, #0xb
		ADD r2, r2, r6
		LDR r6, [pc, #0x130]
		ADD r7, r2, r6
		LDR r2, [sp, #0x18]
		MOV r6, #0x20
		LSL r2, r2, #0x1c
		LSR r2, r2, #0x1b
		SUB r6, r6, r2
		STR r6, [sp, #0xc]
		LSL r6, r1, #6
		ADD r6, r6, r7
		MOV ip, r6
		LDR r6, [r0, #0x14]
		LSL r7, r1, #5
		ADD r6, r6, r7
		MOV lr, r6
		ADD lr, r2
		ADD ip, r2
		ADD r2, r1, #0
		CMP r1, r3
		BGE      |loc_080083CA|
		LDR r6, [sp, #0xc]
		LDR r7, [pc, #0x10c]
		LSL r6, r6, #0xf
		LSR r6, r6, #0x10
		STR r6, [sp, #0x3c]
|loc_080083A6|
		MOV r6, lr
		STR r6, [r7]
		MOV r6, ip
		STR r6, [r7, #4]
		LDR r6, [sp, #0x3c]
		STRH r6, [r7, #8]
		MOV r6, #1
		LSL r6, r6, #0xf
		STRH r6, [r7, #0xa]
		MOV r6, lr
		ADD r6, #0x20
		MOV lr, r6
		MOV r6, ip
		ADD r6, #0x40
		ADD r2, #1
		CMP r2, r3
		MOV ip, r6
		BLT      |loc_080083A6|
|loc_080083CA|
		LSL r2, r5, #0xb
		LSL r6, r4, #5
		MOV ip, r2
		ADD r2, r2, r6
		MOV lr, r6
		LDR r6, [pc, #0xd0]
		ADD r7, r2, r6
		LDR r6, [sp, #0x14]
		STR r7, [sp, #0xc]
		LSL r7, r6, #1
		LDR r2, [sp, #0x10]
		STR r7, [sp, #0x38]
		SUB r2, r2, r6
		LSL r6, r2, #1
		STR r6, [sp, #0x34]
		STR r7, [sp, #8]
		BEQ      |loc_08008436|
		LDR r7, [sp, #0xc]
		LSL r2, r1, #6
		ADD r2, r2, r7
		LDR r7, [sp, #8]
		ADD r2, r2, r7
		STR r2, [sp, #4]
		LDR r2, [r0, #0x18]
		LSL r7, r1, #5
		ADD r2, r2, r7
		LDR r7, [sp, #8]
		ADD r2, r2, r7
		STR r2, [sp]
		ADD r2, r1, #0
		CMP r1, r3
		BGE      |loc_08008436|
		LSL r6, r6, #0xf
		LSR r6, r6, #0x10
		LDR r7, [pc, #0x9c]
		STR r6, [sp, #0x30]
|loc_08008412|
		LDR r6, [sp]
		STR r6, [r7]
		LDR r6, [sp, #4]
		STR r6, [r7, #4]
		LDR r6, [sp, #0x30]
		STRH r6, [r7, #8]
		MOV r6, #1
		LSL r6, r6, #0xf
		STRH r6, [r7, #0xa]
		LDR r6, [sp]
		ADD r2, #1
		ADD r6, #0x20
		STR r6, [sp]
		LDR r6, [sp, #4]
		ADD r6, #0x40
		STR r6, [sp, #4]
		CMP r2, r3
		BLT      |loc_08008412|
|loc_08008436|
		LDR r2, [sp, #0x20]
		CMP r2, #0x10
		BLE      |inc_0x0158_0x143f2| + 0x835a
		MOV r6, #1
		EOR r6, r4
		MOV r2, ip
		LSL r6, r6, #5
		ADD r2, r2, r6
		LDR r6, [pc, #0x60]
		LSL r7, r1, #6
		ADD r2, r2, r6
		LDR r6, [sp, #0x20]
		MOV ip, r7
		ADD ip, r2
		LDR r2, [r0, #0x1c]
		LSL r7, r1, #5
		LSL r6, r6, #1
		SUB r6, #0x20
		ADD r2, r2, r7
		CMP r1, r3
		BGE      |inc_0x0158_0x143f2| + 0x835a
		LSL r6, r6, #0xf
		LSR r6, r6, #0x10
		LDR r7, [pc, #0x44]
		STR r6, [sp, #0x2c]
|loc_08008468|
|unk_08008468|
; cited by 0x080080A8 (a pc-relative load targets 0x08008488)
		STR r2, [r7]
		MOV r6, ip
		STR r6, [r7, #4]
		LDR r6, [sp, #0x2c]
		STRH r6, [r7, #8]
		MOV r6, #1
		LSL r6, r6, #0xf
		STRH r6, [r7, #0xa]
		MOV r6, ip
		ADD r6, #0x40
		ADD r2, #0x20
		ADD r1, #1
		CMP r1, r3
		MOV ip, r6
		B        |inc_0x0158_0x143f2| + 0x8358
	INCBIN  baserom.gba_0x8486_0x84a6.extracted
	CODE16
|dat_080084A6|
	DCW      0x0804
	DCW      0xf000
	DCW      0x0600
	DCW      0x00d4
	DCW      0x0400
	DCW      0xdbda
	DCW      0x9909
	DCW      0x2920
	DCW      0xdd6d
	DCW      0x9909
	DCW      0x9a06
	DCW      0x06c9
	DCW      0x0ec9
	DCW      0x2a00
	DCW      0xda28
	DCW      0x2601
	DCW      0x1c2a
	DCW      0x1c23
	DCW      0x4073
	DCW      0x4072
	DCW      0x02d2
	DCW      0x4ed7
	DCW      0x015b
	DCW      0x18d2
	DCW      0x1993
	DCW      0x9a06
	DCW      0x469c
	DCW      0x0712
	DCW      0x0ed2
	DCW      0x6a03
	DCW      0x2620
	DCW      0x1ab6
	DCW      0x4494
	DCW      0x189a
	DCW      0x2300
	DCW      0x2900
	DCW      0xdd12
	DCW      0x03f6
	DCW      0x0c36
	DCW      0x4fcf
	DCW      0x960a
|loc_080084F8|
	DCW      0x603a
	DCW      0x4666
	DCW      0x607e
	DCW      0x9e0a
	DCW      0x813e
	DCW      0x2601
	DCW      0x03f6
	DCW      0x817e
	DCW      0x4666
	DCW      0x3640
	DCW      0x3220
	DCW      0x3301
	DCW      0x428b
	DCW      0x46b4
	DCW      0xdbf0
|loc_08008516|
	DCW      0x2201
	DCW      0x4055
	DCW      0x02ea
	DCW      0x4694
	DCW      0x4bc4
	DCW      0xaf0d
	DCW      0x4472
	DCW      0x18d2
	DCW      0xcfc0
	DCW      0x2e00
	DCW      0xd015
	DCW      0x6a43
	DCW      0x19d2
	DCW      0x2500
	DCW      0x19db
	DCW      0x2900
	DCW      0xdd0f
	DCW      0x03f6
	DCW      0x0c37
	DCW      0x4ebd
	DCW      0x46be
|loc_08008540|
	DCW      0x6033
	DCW      0x6072
	DCW      0x4677
	DCW      0x8137
	DCW      0x2701
	DCW      0x03ff
	DCW      0x8177
	DCW      0x3320
	DCW      0x3240
	DCW      0x3501
	DCW      0x428d
	DCW      0xdbf3
|loc_08008558|
	DCW      0x9a08
	DCW      0x2a10
	DCW      0xdd1a
	DCW      0x2201
	DCW      0x4054
	DCW      0x0162
	DCW      0x4bb2
	DCW      0x4462
	DCW      0x18d2
	DCW      0x9b08
	DCW      0x2400
	DCW      0x005b
	DCW      0x3b20
	DCW      0x2900
	DCW      0x6a80
	DCW      0xdd0d
	DCW      0x2501
	DCW      0x03ed
	DCW      0x4ead
	DCW      0x03db
	DCW      0x0c1b
|loc_08008582|
	DCW      0x6030
	DCW      0x6072
	DCW      0x8133
	DCW      0x8175
	DCW      0x3020
	DCW      0x3240
	DCW      0x3401
	DCW      0x428c
	DCW      0xdbf6
|loc_08008594|
	DCW      0xb014
	DCW      0xbdf0

