	CODE16
|sub_0803B304|
|unk_0803B304|
		SUB r1, #1
		STRH r1, [r0, #0x12]
		LSR r1, r1, #3
		STRB r1, [r0, #0x11]
		B        |inc_0x351c0_0x3d4d0| + 0x6142
