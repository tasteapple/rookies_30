import re
import os
import time


watch_dir = "./monitor_directory" # 모니터링 할 디렉토리 경로
danger_extensions = ['.py', '.js', '.class'] # 주의 파일 분류 확장자
wait_time = 2 # 디렉토리 검사 주기 (초)
catch_pattern = {
    "주석(Comments)": r"(#.*)|(//.*)|(/\*[\s\S]*?\*/)", # Python(#) 및 C/Java 스타일(//, /**/) 주석 모두 탐지
    "이메일(Email)": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "SQL 구문(SQL Injection 위험)": r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|UNION|JOIN|WHERE|FROM)\s+"
}

def get_all_files_recursive(directory):
    """
    하위 디렉터리까지 포함하여 모든 파일의 상대 경로를 Set으로 반환하는 함수
    예: {'file1.py', 'sub_folder/file2.js', ...}
    """
    file_set = set()
    # os.walk를 사용하여 디렉터리 트리를 순회 (root: 현재 탐색 중인 경로, dirs: 하위 폴더, files: 파일들)
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 파일의 절대 경로 생성
            full_path = os.path.join(root, file)
            # 감시 디렉터리를 기준으로 한 '상대 경로'로 변환하여 저장
            # 이렇게 해야 나중에 analyze_file에서 경로를 합칠 때 문제가 없음
            rel_path = os.path.relpath(full_path, directory)
            file_set.add(rel_path)
    return file_set

def check_directory():
    # 감시하고자 하는 디렉토리의 존재여부 확인(없으면 생성)
    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)
        print(f'[info] Created directory: {watch_dir}')
    
    # 디렉토리 내 기존 파일 목록 저장 및 반환
    file_before = get_all_files_recursive(watch_dir)
    print(f'[info] Monitoring started on directory: {watch_dir} exit with Ctrl+C')
    return file_before
    
def start_monitoring(file_before):
    # 디렉토리 내 파일 변경 감지 및 위험 패턴 검사
    try:
        while True:
            now_files = get_all_files_recursive(watch_dir)
            added_files = now_files - file_before # 새로 추가된 파일 탐지

            if added_files:
                print()
                print("="*20)
                print("file changed!")
                print(f"before: {file_before}")
                print(f"now: {now_files}")
                for filename in added_files:
                    analyze_file(filename)
            
            file_before = now_files # 현재 파일 목록으로 갱신

            time.sleep(wait_time) # 지정된 시간만큼 대기
    except KeyboardInterrupt:
        print('\n[info] Monitoring stopped by user.')
    except Exception as e:
        print(f'[error] An error occurred: {e}')

def analyze_file(filename):
    filepath = os.path.join(watch_dir, filename)
    print(f'\n[info] New file detected: {filename}')

    # splitext 함수를 사용하여 파일 이름과 확장자를 분리
    _, ext = os.path.splitext(filename)

    # 파일 확장자 검사
    if ext in danger_extensions:
        print(f'[warning] detect filter file extension: {ext}')
    else:
        print(f'[info] file extension {ext} is not filtered.')
    
    # 파일 내용 검사
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            scan_sensitive_info(content)
    except UnicodeDecodeError:
        print(f'[error] Could not read file {filename}: Unsupported encoding.')
    except Exception as e:
        print(f'[error] Could not read file {filename}: {e}')

def scan_sensitive_info(content):
    detected = False

    for label, pattern in catch_pattern.items():
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE) # 모든 패턴에 대해 대소문자 구분 없이 멀티라인 모드로 검색
        if matches:
            detected = True
            preview = str(matches[0])[:50] # 첫 번째 매치 결과 미리보기 (최대 50자)
            print(f'[warning] Detected {label}: {preview}...')
            
    if not detected:
        print('[info] No sensitive information detected in file.')

file_before = check_directory()
start_monitoring(file_before)

