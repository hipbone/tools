"""
Terraform instance output을 CSV로 변환하는 스크립트

사용법:
  1. 파일로 입력:
     python tf_vmcreate_output_to_csv.py output.txt
     python tf_vmcreate_output_to_csv.py output.txt result.csv

  2. 파이프로 입력:
     terraform output | python tf_vmcreate_output_to_csv.py

  3. 대화형 붙여넣기 (여러 output 블록 붙여넣기 후 Ctrl+D):
     python tf_vmcreate_output_to_csv.py

지원 포맷:
  instance = {
    "instance-name" = {
      "availability_zone" = "ap-seoul-1"
      "cpu"               = 4
      "disk"              = ["vHDD / 50", "vHDD / 10"]
      "id"                = "ins-xxxxxxxx"
      "memory"            = 8
      "private_ip"        = "10.x.x.x"
      "public_ip"         = "x.x.x.x"
      "state"             = "running"
    }
  }
여러 output 블록을 한 번에 붙여넣어도 됩니다.
"""

import csv
import re
import sys


def parse_tf_instances(text):
    instances = []
    lines = text.splitlines()

    state = "root"
    current_instance = None
    current_list_key = None
    current_list = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if state == "root":
            # "xxx = {" 형태의 outer 블록 시작
            if re.match(r'[\w]+\s*=\s*\{', stripped):
                state = "outer"

        elif state == "outer":
            if stripped == "}":
                state = "root"
            # "instance-name" = { 형태의 인스턴스 블록 시작
            elif re.match(r'"[^"]+"\s*=\s*\{', stripped):
                name = re.match(r'"([^"]+)"', stripped).group(1)
                current_instance = {"name": name}
                state = "instance"

        elif state == "instance":
            if stripped == "}":
                instances.append(current_instance)
                current_instance = None
                state = "outer"
            else:
                m = re.match(r'"([^"]+)"\s*=\s*(.*)', stripped)
                if m:
                    key = m.group(1)
                    val_str = m.group(2).strip()

                    if val_str == "[":
                        current_list_key = key
                        current_list = []
                        state = "list"
                    elif val_str == "null":
                        current_instance[key] = ""
                    elif val_str.startswith('"') and val_str.endswith('"'):
                        current_instance[key] = val_str[1:-1]
                    else:
                        try:
                            current_instance[key] = int(val_str)
                        except ValueError:
                            current_instance[key] = val_str

        elif state == "list":
            if stripped == "]":
                current_instance[current_list_key] = current_list
                state = "instance"
            else:
                item = re.match(r'"([^"]*)",?', stripped)
                if item:
                    current_list.append(item.group(1))

    return instances


def instances_to_csv(instances, csv_filename):
    fieldnames = [
        "name",
        "availability_zone",
        "id",
        "cpu",
        "memory",
        "disk",
        "public_ip",
        "private_ip",
        "state",
        "os",
    ]

    with open(csv_filename, "w", newline="", encoding="UTF-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for inst in instances:
            row = dict(inst)
            if isinstance(row.get("disk"), list):
                row["disk"] = ", ".join(row["disk"])
            if "os" not in row:
                row["os"] = ""
            writer.writerow(row)


def main():
    args = sys.argv[1:]
    input_file = None
    output_file = "instance_info.csv"

    if len(args) >= 1 and not args[0].endswith(".csv"):
        input_file = args[0]
    if len(args) >= 2:
        output_file = args[1]
    elif len(args) == 1 and args[0].endswith(".csv"):
        output_file = args[0]

    # 입력 읽기
    if input_file:
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Terraform output을 붙여넣으세요 (여러 블록 가능). 완료 후 Ctrl+D:")
        print("-" * 60)
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            print("\n취소되었습니다.")
            sys.exit(0)

    instances = parse_tf_instances(text)

    if not instances:
        print("파싱된 인스턴스가 없습니다. 입력 포맷을 확인해주세요.")
        sys.exit(1)

    instances_to_csv(instances, output_file)
    print(f"총 {len(instances)}개 인스턴스 → {output_file} 생성 완료")
    print()
    print(f"{'이름':<30} {'ID':<20} {'IP'}")
    print("-" * 70)
    for inst in instances:
        print(f"{inst.get('name', ''):<30} {inst.get('id', ''):<20} {inst.get('private_ip', '')}")


if __name__ == "__main__":
    main()
