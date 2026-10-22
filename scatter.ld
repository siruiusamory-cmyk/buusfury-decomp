LOAD_ROM_2 0x02000000
{
    EWRAM 0x02000000 0x40000
    {
        ewram.o (+RW)
    }
}
LOAD_ROM_3 0x03000000
{
    IWRAM 0x03000000 0x8000
    {
        iwram.o (+RW)
    }
}
ROM_LOAD 0x08000000 {
	ROM_START 0x08000000
    {
        buu.o (GameStart, Head, Init)
    }
	CPILOT 0x0801c62c
    {
        sub_0801C62C.o (+RO)
    }
	CPILOT2 0x0801c634
    {
        sub_0801C634.o (+RO)
    }
	CPILOT_TAIL 0x0801c63c
    {
        buu.o (CPilotTail)
    }
	CPILOT10 0x0802ad88
    {
        sub_0802AD88.o (+RO)
    }
	CPILOT_TAIL9 0x0802adbc
    {
        buu.o (CPilotTail4)
    }
	CPILOT4 0x0802b960
    {
        sub_0802B960.o (+RO)
    }
	CPILOT_TAIL3 0x0802b974
    {
        buu.o (CPilotTail2)
    }
	CPILOT5 0x0803431c
    {
        sub_0803431C.o (+RO)
    }
	CPILOT_TAIL4 0x08034330
    {
        buu.o (CPilotTail3)
    }
	MEMORY_START 0x0803d4d0
	{
		GBARam.o (GBARam)
	}
	UNUSED_GBARAM 0x0803d740
	{
		buu.o (UnusedGBARam)
	}
	CPILOT8 0x0803e44c
    {
        sub_0803E44C.o (+RO)
    }
	CPILOT9 0x0803e4a0
    {
        sub_0803E4A0.o (+RO)
    }
	CPILOT_TAIL8 0x0803e4e4
    {
        buu.o (UnusedGBARam6)
    }
	CPILOT3 0x08043860
    {
        sub_08043860.o (+RO)
    }
	CPILOT_TAIL2 0x0804386c
    {
        buu.o (UnusedGBARam2)
    }
	CPILOT6 0x08045598
    {
        sub_08045598.o (+RO)
    }
	CPILOT_TAIL5 0x080455b4
    {
        buu.o (UnusedGBARam3)
    }
	CPILOT7 0x08045658
    {
        sub_08045658.o (+RO)
    }
	CPILOT_TAIL6 0x08045670
    {
        buu.o (UnusedGBARam4)
    }
	CPILOT11 0x08046124
    {
        sub_08046124.o (+RO)
    }
	CPILOT12 0x080461f8
    {
        sub_080461F8.o (+RO)
    }
	CPILOT_TAIL10 0x080462ac
    {
        buu.o (UnusedGBARam8)
    }
	AFTER_LIBS 0x08049114
	{
		buu.o (AfterLibs)
	}
	COLOR_TRANSFORMATIONS 0x0805672c
    {
		color_transforms.o (.constdata)
    }
	STRINGS 0x0805792c
    {
		strings.o (+RW +ZI)
    }
	EVERYTHING_ELSE 0x0806d4e0
    {
		rest_of_the_game.o (+Code)
    }
}