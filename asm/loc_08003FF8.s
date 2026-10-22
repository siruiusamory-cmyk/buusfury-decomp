	CODE16
|loc_08003FF8|
|unk_08003FF8|
		MOV r2, #0
|loc_08003FFA|
		LDR r4, [r1]
		LSL r2, r2, #7
		LDRB r3, [r4]
		ADD r4, #1
		STR r4, [r1]
		LSL r4, r3, #0x19
		LSR r4, r4, #0x19
		ADD r2, r2, r4
		LSL r3, r3, #0x18
		BMI      |loc_08003FFA|
		LSL r3, r2, #0x1f
		BPL      |sub_08004018|
		ASR r2, r2, #1
		NEG r3, r2
		B        |inc_0x0158_0x143f2| + 0x3ec2
