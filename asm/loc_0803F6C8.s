	CODE16
|loc_0803F6C8|
|unk_0803F6C8|
		LSL r3, r0, #0x1f
		BPL      |sub_0803F6D2|
		LDRB r3, [r4, #3]
		STRB r3, [r2]
		B        |loc_0803F6DA|
