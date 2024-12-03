import re

# 입력 데이터
file_path = 'data.txt'
with open(file_path, 'r') as file:
    data = file.read()

# 정규 표현식으로 <HOSTNAME>과 시간 추출
# pattern = r"\[Ping Check\] ([\w-]+) - [\d.]+\nTime : \d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2})"

# 정규 표현식으로 <HOSTNAME>만 추출
# pattern = r"\[Ping Check\] ([\w-]+) - [\d.]+\nTime : .*\nStatus : .*\nState : .*\nPoint : .*\nLocation : ([\w]+)\nZone : .*"
pattern = r"\[Ping Check\] ([\w-]+) - [\d.]+\nTime : .*\nStatus : .*\nState : .*\nPoint : .*\nLocation : (.*)\nZone : (.*)"

# 추출된 결과 리스트
results = re.findall(pattern, data)

# 결과를 각각 리스트로 분리
hostnames = [result[0] for result in results]
locations = [result[1] for result in results]
zones = [result[2] for result in results]
location = ','.join(list(set(locations)))
zone = ','.join(list(set(zones)))
hostname = '\n'.join(sorted(list(set(hostnames))))

# 결과 출력
print(f"""location : {location}
zone : {zone}

{hostname}
""")
