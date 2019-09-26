#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, CMake


class LibpngConan(ConanFile):
    name = "libpng"
    upstream_version = "1.6.34"
    package_revision = "-r3"
    version = "{0}{1}".format(upstream_version, package_revision)

    description = "libpng is the official PNG file format reference library."
    homepage = "http://www.libpng.org"
    license = "http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/skip-install-symlink.patch"
    ]
    url = "https://git.ircad.fr/conan/conan-libpng"
    source_subfolder = "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("common/1.0.1@sight/stable")
        if tools.os_info.is_windows:
            self.requires("zlib/1.2.11-r3@sight/stable")

    def source(self):
        tools.get("https://github.com/glennrp/libpng/archive/v{0}.tar.gz".format(self.upstream_version))
        os.rename("libpng-" + self.upstream_version, self.source_subfolder)

    def build(self):
        libpng_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        tools.patch(libpng_source_dir, "patches/skip-install-symlink.patch")

        # Import common flags and defines
        import common

        # Generate Cmake wrapper
        common.generate_cmake_wrapper(
            cmakelists_path='CMakeLists.txt',
            source_subfolder=self.source_subfolder,
            build_type=self.settings.build_type
        )

        cmake = CMake(self)

        cmake.definitions["PNG_TESTS"] = "OFF"
        cmake.definitions["PNG_SHARED"] = self.options.shared
        cmake.definitions["PNG_STATIC"] = not self.options.shared
        cmake.definitions["PNG_DEBUG"] = "OFF" if self.settings.build_type == "Release" else "ON"
        cmake.definitions["SKIP_INSTALL_PROGRAMS"] = "ON"
        cmake.definitions["SKIP_INSTALL_EXECUTABLES"] = "ON"
        if tools.os_info.is_windows or tools.os_info.is_macos:
            cmake.definitions["SKIP_INSTALL_SYMLINK"] = "ON"
        else:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
