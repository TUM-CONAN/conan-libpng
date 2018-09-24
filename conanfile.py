#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, tools, CMake


class LibpngConan(ConanFile):
    name = "libpng"
    version = "1.6.34"
    description = "libpng is the official PNG file format reference library."
    homepage = "http://www.libpng.org"
    license = "http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/CMakeProjectWrapper.txt",
        "patches/skip-install-symlink.patch"
    ]
    requires = "zlib/1.2.11@fw4spl/stable"
    url = "https://gitlab.lan.local/conan/conan-libpng"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.get("https://github.com/glennrp/libpng/archive/v{0}.tar.gz".format(self.version))
        os.rename("libpng-" + self.version, self.source_subfolder)

    def build(self):
        libpng_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        shutil.move("patches/CMakeProjectWrapper.txt", "CMakeLists.txt")
        tools.patch(libpng_source_dir, "patches/skip-install-symlink.patch")
        cmake = CMake(self)
        cmake.definitions["PNG_TESTS"] = "OFF"
        cmake.definitions["PNG_SHARED"] = self.options.shared
        cmake.definitions["PNG_STATIC"] = not self.options.shared
        cmake.definitions["PNG_DEBUG"] = "OFF" if self.settings.build_type == "Release" else "ON"
        cmake.definitions["SKIP_INSTALL_PROGRAMS"] = "ON"
        cmake.definitions["SKIP_INSTALL_EXECUTABLES"] = "ON"
        cmake.definitions["SKIP_INSTALL_SYMLINK"] = "ON"
        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
