# -*- coding: utf-8 -*-

#  @author : @cxy
#  @date : 2025/4/10
#  @github : https://github.com/iHongRen/hpack

import sys
from pack_sign import packSign
from sign_uploader import signUploader
from utils import timeit

@timeit
def main(desc):
    packSign()
    signUploader(desc)


if __name__ == "__main__":   
    desc = sys.argv[1] if len(sys.argv) > 1 else ''
    main(desc)





