# Ship the side module as libopenal.wasm, without soname versioning
set(CMAKE_SHARED_LIBRARY_SUFFIX ".wasm")
set(CMAKE_PLATFORM_NO_VERSIONED_SONAME ON)
