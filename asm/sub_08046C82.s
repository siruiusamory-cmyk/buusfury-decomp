	CODE16
|sub_08046C82|
|unk_08046C82|
		LSL r3, r2, #0x1f
		BPL      |loc_08046C8A|
		ADD r2, #1
		B        |loc_08046C96|
|loc_08046C8A|
		LDRB r3, [r0]
		LDRB r4, [r1]
		ADD r1, #1
		ADD r0, #1
		CMP r3, r4
		BNE      |loc_08046CA6|
|loc_08046C96|
		LDRB r3, [r0]
		LDRB r4, [r1]
		ADD r1, #1
		ADD r0, #1
		CMP r3, r4
		BNE      |loc_08046CA6|
		SUB r2, #2
		BNE      |loc_08046C8A|
|loc_08046CA6|
		SUB r0, r3, r4
		DCW     0xE7E9
