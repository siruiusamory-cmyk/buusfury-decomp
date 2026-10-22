	CODE16
|sub_08048076|
|unk_08048076|
		LDR r0, [pc, #0x90]
		AND r0, r1
		BEQ      |loc_08048080|
		DCW     0xA423
		B        |loc_080480AE|
|loc_08048080|
		LSL r0, r1, #3
		BPL      |loc_08048088|
		DCW     0xA425
		B        |loc_080480AE|
|loc_08048088|
		LSL r0, r1, #2
		BPL      |loc_08048090|
		DCW     0xA426
		B        |loc_080480AE|
|loc_08048090|
		LSL r0, r1, #1
		BPL      |loc_080480AE|
		DCW     0xA427
		B        |loc_080480AE|
|loc_08048098|
|unk_08048098|
		CMP r0, #8
		BNE      |loc_080480A0|
		ADD r4, r1, #0
		B        |loc_080480AE|
|loc_080480A0|
		CMP r0, #9
		BNE      |loc_080480AE|
		CMP r1, #1
		BNE      |loc_080480AE|
		DCW     0xA526
		B        |loc_080480AE|
