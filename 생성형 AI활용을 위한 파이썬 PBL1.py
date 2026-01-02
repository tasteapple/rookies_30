class StudentScores:
    def __init__(self, filename: str): # filename : 성적 데이터 파일 이름
        self.filename = filename
        self.__student_scores = {} # 학생 이름 : 키, 점수 : 값, private 변수로 설정해서 캡슐화 진행
        try:
            with open(self.filename, 'r') as f:
                for line in f:
                    name, score = line.strip().split(',') # ,로 이름과 점수 분리
                    self.__student_scores[name] = int(score) # 점수를 정수형으로 변환하여 딕셔너리에 저장
        except FileNotFoundError:
            print(f'Cannot find file: {self.filename}')
        except Exception as e:
            print('Error reading file:', e)
    
    # 평균 점수 계산
    def calculate_average(self) -> float:
        if not self.__student_scores:
            return "No scores available"
        avgerage = sum(self.__student_scores.values()) / len(self.__student_scores) # 딕셔너리에서 values() 메서드로 점수들만 추출하여 합산 후 학생 수로 나누기
        return avgerage
    
    # 평균 점수 이상인 학생들 이름 반환
    def get_above_average(self) -> list:
        average = self.calculate_average()
        if type(average) == str: # 평균 점수가 문자열인 경우(즉, "No scores available"인 경우)
            return "No scores available"
        above_students = [name for name, score in self.__student_scores.items() if score > average] # 리스트 컴프리헨션을 사용해서 평균 이상인 학생 이름들만 추출
        return above_students
    
    def save_below_average(self, output_filename="below_average_Korean.txt"): # 파일 이름을 지정하지 않으면 기본값으로 "below_average_Korean.txt" 사용
        average = self.calculate_average()
        if type(average) == str: # 평균 점수가 문자열인 경우(즉, "No scores available"인 경우)
            return "No scores available"
        try:
            with open(output_filename, 'w') as f:
                for name, score in self.__student_scores.items():
                    if score < average:
                        f.write(f'{name}, {score}\n') # 평균 이하인 학생 이름과 점수를 파일에 저장
        except Exception as e:
            print('Error writing to file:', e)
        
    def print_summary(self):
        average = self.calculate_average()
        if type(average) == str: # 평균 점수가 문자열인 경우(즉, "No scores available"인 경우)
            print(average)
            return
        above_students = self.get_above_average()
        print(f'Average Score: {average:.2f}')
        print(f'Students above average: {above_students}')


if __name__ == "__main__":
    students = StudentScores('scores_Korean.txt')
    # print(students.calculate_average())
    # print(students.get_above_average())
    students.save_below_average()
    students.print_summary()