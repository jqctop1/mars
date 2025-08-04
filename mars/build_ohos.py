#!/usr/bin/env python3
import os
import sys
import glob
import time
import shutil
import platform

from mars_utils import *


SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]

try:
    NDK_ROOT = os.environ['OHOS_NDK_ROOT']
except KeyError as identifier:
    NDK_ROOT = ''


BUILD_OUT_PATH = 'cmake_build/ohos'
LIBS_INSTALL_PATH = BUILD_OUT_PATH + '/'
BUILD_CMD = 'cmake  %s -DOHOS_ARCH="%s" -DOHOS_PLATFORM=OHOS ' \
                    '-DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=%s/build/cmake/ohos.toolchain.cmake ' \
                    '-DOHOS_STL="c++_shared" ' \
                    '&& cmake --build . %s'
SYMBOL_PATH = 'libraries/mars_ohos_sdk/obj/local/'
LIBS_PATH = 'libraries/mars_ohos_sdk/libs/'
XLOG_SYMBOL_PATH = 'libraries/mars_xlog_sdk/obj/local/'
XLOG_LIBS_PATH = 'libraries/mars_xlog_sdk/libs/'


STL_FILE = {
        'armeabi-v7a': NDK_ROOT + '/llvm/lib/arm-linux-ohos/libc++_shared.so',
        'arm64-v8a': NDK_ROOT + '/llvm/lib/aarch64-linux-ohos/libc++_shared.so',
}


def build_ohos(incremental, arch, target_option=''):

    before_time = time.time()
    
    clean(BUILD_OUT_PATH, incremental)
    os.chdir(BUILD_OUT_PATH)
    
    build_cmd = BUILD_CMD %(SCRIPT_PATH, arch, NDK_ROOT, target_option)
    print("build cmd:" + build_cmd)
    ret = os.system(build_cmd)
    os.chdir(SCRIPT_PATH)

    if 0 != ret:
        print('!!!!!!!!!!!!!!!!!!build fail!!!!!!!!!!!!!!!!!!!!')
        return False

    if len(target_option) > 0:
        symbol_path = XLOG_SYMBOL_PATH
        lib_path = XLOG_LIBS_PATH
    else:
        symbol_path = SYMBOL_PATH
        lib_path = LIBS_PATH

    if not os.path.exists(symbol_path):
        os.makedirs(symbol_path)

    symbol_path = symbol_path + arch
    if os.path.exists(symbol_path):
        shutil.rmtree(symbol_path)

    os.mkdir(symbol_path)


    if not os.path.exists(lib_path):
        os.makedirs(lib_path)

    lib_path = lib_path + arch
    if os.path.exists(lib_path):
        shutil.rmtree(lib_path)

    os.mkdir(lib_path)


    for f in glob.glob(LIBS_INSTALL_PATH + "*.so"):
        shutil.copy(f, symbol_path)
        shutil.copy(f, lib_path)

    # copy stl
    shutil.copy(STL_FILE[arch], symbol_path)
    shutil.copy(STL_FILE[arch], lib_path)

    print('==================Output========================')
    print('libs(release): %s' %(lib_path))
    print('symbols(must store permanently): %s' %(symbol_path))


    after_time = time.time()

    print("use time:%d s" % (int(after_time - before_time)))
    return True

def main(incremental, archs, target_option='', tag=''):
    if not check_ohos_ndk_env():
        return

    gen_mars_revision_file(SCRIPT_PATH + '/comm', tag)

    for arch in archs:
        if not build_ohos(incremental, arch, target_option):
            return

if __name__ == '__main__':

    while True:
        if len(sys.argv) >= 3:
            archs = sys.argv[2:]
            main(False, archs, tag=sys.argv[1])
            break
        else:
            archs = {'armeabi-v7a', 'arm64-v8a'}
            num = input('Enter menu:\n1. Clean && build mars.\n2. Build incrementally mars.\n3. Clean && build xlog.\n4. Exit\n')
            if num == '1':
                main(False, archs)
                break
            elif num == '2':
                main(True, archs)
                break
            elif num == '3':
                main(False, archs, '--target libzstd_static marsxlog')
                break
            elif num == '4':
                break
            else:
                main(False, archs)
                break


