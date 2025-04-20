import argparse
import json  
import os
import sys  # 添加 sys 模块
import oss2

from config import Config

def packBefore():
    print("============开始打包=============")

def packAfter():
    # 从标准输入读取 JSON 数据
    try:
        result_json = sys.stdin.read()
        result = json.loads(result_json)
    except json.JSONDecodeError as e:
        print(f"解析 JSON 数据时出错: {e}")
        return
    except Exception as e:
        print(f"读取标准输入时出错: {e}")
        return

    # 打包完成后，上传到 OSS， 你也可以上传到自己的服务器
    upload_to_oss(Config, result)

    print("============打包信息:============")
    print(json.dumps(result, indent=4, ensure_ascii=False))
    print("================================")

    url = result["url"]
    print(f"\033[0m请访问 {url}\033[0m")


def upload_to_oss(Config, result):
    build_dir = result["build_dir"]
    timestamp = result["timestamp"]
   
    # 上传 hpack/build 目录里的打包文件到 OSS
    if len(os.listdir(build_dir)) == 0:
        print(f"无法上传空的目录 {build_dir}")
        return False

    auth = oss2.Auth(Config.Access_key_id, Config.Access_key_secret)
    bucket = oss2.Bucket(auth, Config.Endpoint, Config.Bucket_name)

    for root, _, files in os.walk(build_dir):
        for file in files:
            if file == "unsign_manifest.json5":
                continue
            
            file_path = os.path.join(root, file)
            try:
                print(f"正在上传： {file} ")
                romotePath = f"{Config.Bucket_dir}/{timestamp}/{file}"
                result = bucket.put_object_from_file(romotePath, file_path)
                if result.status == 200:
                    print(f"文件 {file} 上传到 OSS 成功。")      
                else:
                    print(f"文件 {file} 上传到 OSS 失败，状态码: {result.status}。")

            except Exception as e:
                print(f"文件 {file} 上传到 OSS 时出现异常: {e}。")
                return False

    print("\033[34m所有文件上传到 OSS 成功。\033[0m")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Packfile script")
    parser.add_argument('--before', action='store_true', help="Execute packBefore")
    parser.add_argument('--after', action='store_true', help="Execute packAfter")
    args = parser.parse_args()

    if args.before:
        packBefore()
    elif args.after:
        packAfter()  # 不再需要通过命令行参数传递 JSON 数据
    else:
        print("No valid action specified.")