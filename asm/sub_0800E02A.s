	CODE16
|sub_0800E02A|
|unk_0800E02A|
		MOV r0, #4
		STRB r0, [r1, #0x11]
		B        |inc_0x0158_0x143f2| + 0xded0
|loc_0800E030|
|unk_0800E030|
		CMP r2, #0x20
		BHS      |loc_0800E03A|
		LSR r0, r2, #4
		STRB r0, [r1, #0x11]
		B        |inc_0x0158_0x143f2| + 0xded0
|loc_0800E03A|
		LSL r0, r2, #0x1b
		LSR r0, r0, #0x1f
		ADD r0, #2
		STRB r0, [r1, #0x11]
		B        |inc_0x0158_0x143f2| + 0xded0
