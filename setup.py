#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Build and install the TweetNaCl wrapper.
"""

import sys, os
from distutils.core import setup, Extension, Command
from distutils.util import get_platform

def setup_path():
    # copied from distutils/command/build.py
    plat_name = get_platform()
    plat_specifier = ".%s-%s" % (plat_name, sys.version[0:3])
    build_lib = os.path.join("build", "lib"+plat_specifier)
    sys.path.insert(0, build_lib)

nacl_module = Extension('nacl._tweetnacl',
                        ["tweetnaclmodule.c", "tweetnacl.c", "randombytes.c"],
                        extra_compile_args=["-O2",
                                            "-funroll-loops",
                                            "-fomit-frame-pointer"])

class Test(Command):
    description = "run tests"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        setup_path()
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "test"))
        import test_box; test_box.run()
        import test_box_curve25519xsalsa20poly1305; test_box_curve25519xsalsa20poly1305.run()
        import test_hash; test_hash.run()
        import test_hash_sha512; test_hash_sha512.run()
        import test_onetimeauth; test_onetimeauth.run()
        import test_onetimeauth_poly1305; test_onetimeauth_poly1305.run()
        import test_scalarmult; test_scalarmult.run()
        import test_scalarmult_curve25519; test_scalarmult_curve25519.run()
        import test_secretbox; test_secretbox.run()
        import test_secretbox_xsalsa20poly1305; test_secretbox_xsalsa20poly1305.run()
        import test_sign; test_sign.run()
        import test_sign_ed25519; test_sign_ed25519.run()
        import test_stream; test_stream.run()
        import test_stream_salsa20; test_stream_salsa20.run()
        import test_stream_xsalsa20; test_stream_xsalsa20.run()
        import test_verify_16; test_verify_16.run()
        import test_verify_32; test_verify_32.run()

class Speed(Test):
    description = "run benchmark suite"
    def run(self):
        setup_path()
        from timeit import main
        IM = "from nacl import raw; msg='H'*1000"

        # Hash
        S1 = "raw.crypto_hash(msg)"
        sys.stdout.write(" Hash: ")
        main(["-n", "10000", "-s", IM, S1])

        # OneTimeAuth
        S1 = "k = 'k'*raw.crypto_onetimeauth_KEYBYTES"
        S2 = "auth = raw.crypto_onetimeauth(msg, k)"
        S3 = "raw.crypto_onetimeauth_verify(auth, msg, k)"
        sys.stdout.write(" OneTimeAuth: ")
        main(["-n", "10000", "-s", ";".join([IM, S1]), S2])
        sys.stdout.write(" OneTimeAuth verify: ")
        main(["-n", "10000", "-s", ";".join([IM, S1, S2]), S3])

        # SecretBox
        S1 = "k = 'k'*raw.crypto_secretbox_KEYBYTES"
        S2 = "nonce = raw.randombytes(raw.crypto_secretbox_NONCEBYTES)"
        S3 = "c = raw.crypto_secretbox(msg, nonce, k)"
        S4 = "raw.crypto_secretbox_open(c, nonce, k)"
        sys.stdout.write(" Secretbox encryption: ")
        main(["-n", "10000", "-s", ";".join([IM, S1, S2]), S3])
        sys.stdout.write(" Secretbox decryption: ")
        main(["-n", "10000", "-s", ";".join([IM, S1, S2, S3]), S4])

        # Curve25519
        S1 = "pk,sk = raw.crypto_box_keypair()"
        S2 = "nonce = raw.randombytes(raw.crypto_box_NONCEBYTES)"
        S3 = "ct = raw.crypto_box(msg, nonce, pk, sk)"
        S4 = "k = raw.crypto_box_beforenm(pk, sk)"
        S5 = "ct = raw.crypto_box_afternm(msg, nonce, k)"

        sys.stdout.write(" Curve25519 keypair generation: ")
        main(["-n", "1000", "-s", IM, S1])
        sys.stdout.write(" Curve25519 encryption: ")
        main(["-n", "1000", "-s", ";".join([IM, S1, S2, S3]), S3])
        sys.stdout.write(" Curve25519 beforenm (setup): ")
        main(["-n", "1000", "-s", ";".join([IM, S1, S2, S3]), S4])
        sys.stdout.write(" Curve25519 afternm: ")
        main(["-n", "10000", "-s", ";".join([IM, S1, S2, S3, S4]), S5])

        # Ed25519
        S1 = "vk,sk = raw.crypto_sign_keypair()"
        S2 = "sig = raw.crypto_sign(msg, sk)"
        S3 = "raw.crypto_sign_open(sig, vk)"

        sys.stdout.write(" Ed25519 keypair generation: ")
        main(["-n", "1000", "-s", IM, S1])
        sys.stdout.write(" Ed25519 signing: ")
        main(["-n", "1000", "-s", ";".join([IM, S1]), S2])
        sys.stdout.write(" Ed25519 verifying: ")
        main(["-n", "1000", "-s", ";".join([IM, S1, S2]), S3])


setup (name = 'tweetnacl',
       version = '0.1',
       author      = "Brian Warner, Jan Mojžíš",
       description = """Python wrapper for TweetNaCl""",
       ext_modules = [nacl_module],
       packages = ["nacl"],
       package_dir = {"nacl": "src"},
       cmdclass = { "test": Test,
                    "speed": Speed },
       )
