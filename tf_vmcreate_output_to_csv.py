import csv

data = [
    {
    "availability_zone" = "ap-northeast-1a"
    "cpu" = 2
    "disk" = [
      "vHDD / 50",
      "vHDD / 10",
    ]
    "id" = "i-0d799d0738c5b25bc"
    "memory" = 4
    "private_ip" = "10.30.31.142"
    "public_ip" = "43.206.205.45"
    "state" = "running"
  }
]


# CSV 파일로 데이터 쓰기
## Windows : "D:\output\instance_info.csv"
csv_filename = "instance_info.csv"

with open(csv_filename, "w", newline="", encoding="UTF-8") as csv_file:
    fieldnames = [
        "availability_zone",
        "name",
        "cpu",
        "memory",
        "disk",
        "public_ip",
        "private_ip",
        "os",
        "id",
    ]
    csv_writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames,
    )

    csv_writer.writeheader()
    for info in data:
        info["disk"] = " / ".join(info["disk"])
        csv_writer.writerow(info)

print(f"CSV 파일 {csv_filename}이 생성되었습니다.")
