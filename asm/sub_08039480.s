	CODE16
|sub_08039480|
	PUSH     {lr}
	SUB      sp, #0x14
	MOV      r1, #0
	LDR      r0, [pc, #0xdc]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0xf
	LSL      r2, r2, #8
	MOV      r1, #0
	LDR      r0, [pc, #0xd4]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #9
	STR      r0, [sp, #4]
	MOV      r0, #8
	STR      r0, [sp, #8]
	MOV      r0, #0x15
	STR      r0, [sp, #0xc]
	MOV      r0, #0xd
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0xc0]
	LDR      r1, [pc, #0xb4]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r1, #0x3f
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	LSL      r1, r1, #7
	STRH     r1, [r0, #8]
	LDRH     r1, [r0]
	LSR      r2, r0, #0x12
	ORR      r1, r2
	STRH     r1, [r0]
	ADD      sp, #0x14
	POP      {pc}
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1a
	LDRH     r1, [r3]
	LSR      r2, r3, #0x12
	BIC      r1, r2
	STRH     r1, [r3]
	CMP      r0, #0
	BEQ      |loc_080394E6|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080394E6|
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0x28
	MOV      r1, #0x60
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	MOV      r0, #1
	ADD      r3, sp, #0
	STRB     r0, [r3]
	STRB     r0, [r3, #2]
	LDR      r0, [pc, #0x64]
	STR      r0, [sp, #0x20]
	LDR      r0, [pc, #0x64]
	LDR      r0, [r0]
	STR      r0, [sp, #0xc]
	MOV      r0, #0x30
	STR      r0, [sp, #4]
	MOV      r0, #0x14
	STR      r0, [sp, #8]
	MOV      r0, #2
	STRB     r0, [r3, #3]
	LDR      r0, [pc, #0x58]
	LDR      r1, [r0, #0x20]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x34]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	ADD      r2, r0, #0
	PUSH     {r3, lr}
	LDR      r3, [r1, #0x20]
	LDR      r0, [pc, #0x20]
	LDR      r1, [r1, #0x14]
	ADD      r2, #0xff
	ADD      r2, #0x19
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x480a
	MOV      r0, #1
	POP      {r3, pc}
|sub_08039562|
|unk_08039562|
	INCBIN	baserom.gba_0x39562_0x39566.extracted
	CODE16
|dat_08039566|
	DCW      0x0600
	DCW      0x9640
	DCW      0x0600
	DCW      0x0259
	DCW      0x0000
	DCW      0xf5a5
	DCW      0x0803
	DCW      0xaf30
	DCW      0x0877
	DCW      0xbce8
	DCW      0x0806
	DCW      0xb5f0
	DCW      0x1c04
	DCW      0x486f
	DCW      0xb085
	DCW      0x6e45
	DCW      0x6e86
	DCW      0x2200
	DCW      0x9203
	DCW      0x223c
	DCW      0x9200
	DCW      0x2000
	DCW      0x2101
	DCW      0x9102
	DCW      0x2200
	DCW      0x230c
	DCW      0x1c21
	DCW      0x9001
	DCW      0xf7da
	DCW      0xfc61
	DCW      0x1c01
	DCW      0x1c20
	DCW      0xf7cd
	DCW      0xf852
	DCW      0x4866
	DCW      0x2100
	DCW      0x6882
	DCW      0x2748
	DCW      0x1c3b
	DCW      0x9102
	DCW      0x2005
	DCW      0x9203
	DCW      0x221c
	DCW      0x9001
	DCW      0x1c21
	DCW      0x2000
	DCW      0x9500
	DCW      0xf7da
	DCW      0xfdae
	DCW      0x1c01
	DCW      0x1c20
	DCW      0xf7cd
	DCW      0xf83f
	DCW      0x485c
	DCW      0x1c29
	DCW      0x6880
	DCW      0xf006
	DCW      0xfd07
	DCW      0x2200
	DCW      0x9203
	DCW      0x1c05
	DCW      0x2101
	DCW      0x351e
	DCW      0x223c
	DCW      0x9200
	DCW      0x1c2b
	DCW      0x9101
	DCW      0x9102
	DCW      0x1c21
	DCW      0x2201
	DCW      0x2000
	DCW      0xf7da
	DCW      0xfc36
	DCW      0x1c01
	DCW      0x1c20
	DCW      0xf7cd
	DCW      0xf827
	DCW      0x4850
	DCW      0x2100
	DCW      0x6882
	DCW      0x9102
	DCW      0x9203
	DCW      0x1c2a
	DCW      0x3210
	DCW      0x2005
	DCW      0x1c3b
	DCW      0x1c21
	DCW      0x9001
	DCW      0x2000
	DCW      0x9600
	DCW      0xf7da
	DCW      0xfd83
	DCW      0x1c01
	DCW      0x1c20
	DCW      0xf7cd
	DCW      0xf814
	DCW      0x2201
	DCW      0x02d2
	DCW      0x2100
	DCW      0x4846
	DCW      0xf00f
	DCW      0xfd7d
	DCW      0x2237
	DCW      0x0212
	DCW      0x2100
	DCW      0x4844
	DCW      0xf00f
	DCW      0xfd77
	DCW      0x2005
	DCW      0x9001
	DCW      0x9002
	DCW      0x2019
	DCW      0x9003
	DCW      0x2010
	DCW      0x9004
	DCW      0xa801
	DCW      0x4a40
	DCW      0x493d
	DCW      0xf004
	DCW      0xf9dd
	DCW      0x213f
	DCW      0x2001
	DCW      0x0680
	DCW      0x01c9
	DCW      0x8101
	DCW      0x8801
	DCW      0x0c82
	DCW      0x4311
	DCW      0x8001
	DCW      0xb005
	DCW      0xbdf0
	DCW      0xb508
	DCW      0x2301
	DCW      0x069b
	DCW      0x8819
	DCW      0x0c9a
	DCW      0x4391
	DCW      0x8019
	DCW      0x2800
	DCW      0xd005
	DCW      0x6801
	DCW      0x680a
	DCW      0x1852
	DCW      0x2101
	DCW      0xf00d
	DCW      0xfa0d
|loc_0803968A|
	DCW      0xbd08
	DCW      0xb5f0
	DCW      0xb08d
	DCW      0x1c07
	DCW      0x2258
	DCW      0x21a0
	DCW      0x4668
	DCW      0x466c
	DCW      0xf005
	DCW      0xff51
	DCW      0x1c20
	DCW      0xf7cb
	DCW      0xfcf9
	DCW      0x2001
	DCW      0xab00
	DCW      0x7018
	DCW      0x7098
	DCW      0x4829
	DCW      0x4d25
	DCW      0x9008
	DCW      0x2050
	DCW      0x9001
	DCW      0x2014
	DCW      0x9002
	DCW      0x6868
	DCW      0x4e20
	DCW      0x9003
	DCW      0x2003
	DCW      0x70d8
	DCW      0x6af1
	DCW      0x1c20
	DCW      0xf004
	DCW      0xfa07
	DCW      0x68a8
	DCW      0xab00
	DCW      0x9003
	DCW      0x2050
	DCW      0x9001
	DCW      0x202c
	DCW      0x9002
	DCW      0x200c
	DCW      0x7058
	DCW      0x2002
	DCW      0x70d8
	DCW      0x2184
	DCW      0x1c20
	DCW      0x6ef2
	DCW      0xf004
	DCW      0xfb3d
	DCW      0x1c21
	DCW      0x1c38
	DCW      0xf7cc
	DCW      0xfffc
	DCW      0x4915
	DCW      0x1c20
	DCW      0xf00f
	DCW      0xfd2a
	DCW      0x2100
	DCW      0x4668
	DCW      0xf005
	DCW      0xff44
	DCW      0xb00d
	DCW      0xbdf0
	DCW      0x490e
	DCW      0xb508
	DCW      0x6809
	DCW      0x4812
	DCW      0x2300
	DCW      0x1808
	DCW      0x4911
	DCW      0x2a00
	DCW      0xd009
	DCW      0x2a01
	DCW      0xd10d
	DCW      0x2240
	DCW      0xf004
	DCW      0xfe2a
	DCW      0x2001
	DCW      0xf004
	DCW      0xf8a6
	DCW      0x2001
	DCW      0xbd08

