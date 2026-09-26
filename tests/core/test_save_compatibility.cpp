#include "Core/SaveCompatibility.h"
#include <cassert>
#include <iostream>
int main(){using survival::ResolveSaveFormat;
 for(int version=1;version<=8;++version)assert(ResolveSaveFormat(version,9,17)==version);
 assert(ResolveSaveFormat(0,9,17)==8);assert(ResolveSaveFormat(0,0,17)==5);assert(ResolveSaveFormat(0,0,0)==1);assert(ResolveSaveFormat(0,3,17)==0);assert(ResolveSaveFormat(99,9,17)==99);
 std::cout<<"SAVE_COMPATIBILITY_PASS explicit_versions omitted_legacy_marker malformed_shape\n";
}
