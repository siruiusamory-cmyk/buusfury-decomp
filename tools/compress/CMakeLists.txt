cmake_minimum_required(VERSION 3.17)
project(compress CXX)

set(CMAKE_CXX_STANDARD 14)
enable_language(ASM_MASM)

add_executable(compress main.cpp jcalg1/jcalg1_static.asm)
target_include_directories(compress PRIVATE jcalg1)
target_link_options(compress PRIVATE /SAFESEH:NO)
