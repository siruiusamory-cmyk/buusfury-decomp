	CODE16
|sub_0802AB3A|
|unk_0802AB3A|
		CMP r0, #0x38
		BHS      |loc_0802AB4A|
		ADD r0, #8
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1f
		ADD r0, #1
		STRB r0, [r4, #0x11]
		B        |loc_0802AB36|
|loc_0802AB4A|
		CMP r0, #0x48