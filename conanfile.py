#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, CMake


class LibpngConan(ConanFile):
    python_requires = "camp_common/[>=0.1]@camposs/stable"
    python_requires_extend = "camp_common.CampCMakeBase"

    name = "libpng"
    upstream_version = "1.6.34"
    package_revision = "-r4"
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
        if tools.os_info.is_windows:
            self.requires("zlib/1.2.11-r1@camposs/stable")

    def source(self):
        tools.get("https://github.com/glennrp/libpng/archive/v{0}.tar.gz".format(self.upstream_version))
        os.rename("libpng-" + self.upstream_version, self.source_subfolder)

    def _before_configure(self):
        libpng_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        tools.patch(libpng_source_dir, "patches/skip-install-symlink.patch")

        # Import common flags and defines
        common = self.python_requires["camp_common"].module

        # Generate Cmake wrapper
        common.generate_cmake_wrapper(
            cmakelists_path='CMakeLists.txt',
            source_subfolder=self.source_subfolder,
            build_type=self.settings.build_type
        )

    def _before_build(self, cmake):
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
