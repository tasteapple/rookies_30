import re
import os
import csv
from collections import Counter

# 사용자로부터 파일의 경로를 입력 받는다
def get_file_path():
    while True:
        file_path = input("Enter the path of the log file: ").strip()
        if os.path.exists(file_path):
            return file_path
        else:
            print("File does not exist. Please try again.")

def analyze_log_file_and_top3(file_path):
    # ipv4 정규식 패턴
    ipv4_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    ip_list = []
    # 로그에서 등장하는 모든 IP를 리스트에 저장 (중복 허용)
    try:
        with open(file_path, 'r') as f:
            for line in f:
                ips = ipv4_pattern.findall(line) # 한 줄에 여러 IP가 있을 수 있으므로 모두 찾기
                ip_list.extend(ips)
    except Exception as e:
        print('Error reading file:', e)
        return
    
    ip_count = Counter(ip_list)  # IP 등장 횟수 세기
    print("IP Count:", ip_count)
    top3_ips = ip_count.most_common(3)  # 등장 횟수 기준 상위 3개 IP 추출
    print("Top 3 IPs:", top3_ips)
    return ip_count, top3_ips

def save_ip_count_to_csv(ip_count, top3_ips, output_filename="ip_analysis.csv"):
    try:
        with open(output_filename, 'w', encoding='utf-8-sig', newline='') as csvfile:
            fieldnames = ['IP Address', 'Count'] # CSV 헤더 정의
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader() # 헤더 작성
            # 모든 IP와 그 등장 횟수 저장
            for ip, count in ip_count.items():
                writer.writerow({'IP Address': ip, 'Count': count})

            # 상위 3개 IP를 별도로 저장
            writer.writerow({})
            writer.writerow({'IP Address': 'Top 3 IPs', 'Count': ''})
            for ip, count in top3_ips:
                writer.writerow({'IP Address': ip, 'Count': count})
    except Exception as e:
        print('Error writing to CSV file:', e)

if __name__ == "__main__":
    file_path = get_file_path()
    ip_count, top3_ips = analyze_log_file_and_top3(file_path)
    if ip_count and top3_ips:
        save_ip_count_to_csv(ip_count, top3_ips)
        print(f'IP analysis saved to ip_analysis.csv')