	CODE16
|sub_08029584|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x3c]
	ADD      r7, r3, #0
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	SUB      r4, #0xc
	LDR      r0, [r4, #4]
	SUB      sp, #4
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_080295B6|
	ADD      r3, r5, #0
	ADD      r2, r6, #0
	MOV      r0, #0
	STR      r7, [sp]
	LDR      r1, [sp, #4]
	BL       |loc_08029384|
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_080295B6|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
|unk_080295BC|
	INCBIN	baserom.gba_0x295bc_0x295be.extracted
|dat_080295BE|
	DCW      0x0804
	DCW      0x01ec
	DCW      0x0875
	DCW      0xf08c
	DCW      0x0874
	DCW      0x9440
	DCW      0x0831
	DCW      0x05c4
	DCW      0x0000
	DCW      0x0204
	DCW      0x0875
	DCW      0x80d8
	DCW      0x086b
	DCW      0x92a8
	DCW      0x0831
	DCW      0xb570
	DCW      0x1c05
	DCW      0x4828
	DCW      0x1c0e
	DCW      0x6801
	DCW      0x2400
	DCW      0x2900
	DCW      0xb090
	DCW      0xd035
	DCW      0xa802
	DCW      0xf7e6
	DCW      0xfc03
	DCW      0x9802
	DCW      0x9904
	DCW      0x9a05
	DCW      0x1841
	DCW      0x9803
	DCW      0x9100
	DCW      0x1880
	DCW      0x9001
	DCW      0x1040
	DCW      0x1049
	DCW      0x9100
	DCW      0x9106
	DCW      0x9001
	DCW      0x9007
	DCW      0xa808
	DCW      0x1c31
	DCW      0xf7e6
	DCW      0xfbf1
	DCW      0x9808
	DCW      0x990a
	DCW      0x9a0b
	DCW      0x1841
	DCW      0x9809
	DCW      0x9100
	DCW      0x1880
	DCW      0x9001
	DCW      0x1040
	DCW      0x9001
	DCW      0x900d
	DCW      0x1049
	DCW      0x9806
	DCW      0x9100
	DCW      0x910c
	DCW      0x1a41
	DCW      0x9807
	DCW      0x9a0d
	DCW      0x9100
	DCW      0x1a80
	DCW      0x9001
	DCW      0x900f
	DCW      0x1c08
	DCW      0x4348
	DCW      0x910e
	DCW      0x990f
	DCW      0x1c0a
	DCW      0x4351
	DCW      0x1840
	DCW      0x68e9
	DCW      0x4288
	DCW      0xdd00
	DCW      0x2401
|loc_0802965A|
	DCW      0x1c20
	DCW      0xb010
	DCW      0xbd70
	DCW      0xb538
	DCW      0x68c5
	DCW      0x6900
	DCW      0x6802
	DCW      0xf01d
	DCW      0xfa1c
	DCW      0x1c04
	DCW      0x2010
	DCW      0xf013
	DCW      0xffa2
	DCW      0x2800
	DCW      0xd003
	DCW      0x4903
	DCW      0xc012
	DCW      0x3808
	DCW      0x60c5
|loc_08029680|
	DCW      0xbd38
	DCW      0x0000
	DCW      0x1b94
	DCW      0x0300
	DCW      0xa6e8
	DCW      0x0804
	DCW      0xb510
	DCW      0x68c4
	DCW      0x2008
	DCW      0xf013
	DCW      0xff91
	DCW      0x2800
	DCW      0xd002
	DCW      0x4905
	DCW      0xc012
	DCW      0x3808
|loc_080296A0|
	DCW      0xbd10
	DCW      0x68c0
	DCW      0x31ff
	DCW      0x31c1
	DCW      0x6248
	DCW      0x2000
	DCW      0x4770
|sub_080296AE|
|unk_080296AE|
	INCBIN	baserom.gba_0x296ae_0x296b2.extracted
