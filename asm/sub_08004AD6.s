	CODE16
|sub_08004AD6|
|unk_08004AD6|
		ADD r0, #1
		CMP r7, r0
		BGT      |inc_0x0158_0x143f2| + 0x4950
|loc_08004ADC|
|unk_08004ADC|
		ADD r4, #1
		CMP ip, r4
		BGT      |inc_0x0158_0x143f2| + 0x4942
		B        |loc_08004AD2|
	INCBIN  baserom.gba_0x4ae4_0x4ae6.extracted
