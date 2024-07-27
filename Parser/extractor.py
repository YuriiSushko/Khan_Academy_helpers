import csv
from typing import List, Dict
import os
from Parser.base_functions import BaseKhanDataHandling
from Parser.base_functions import KhanDataHandling


class ExtractAndExportToCsv(BaseKhanDataHandling):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extractor(self) -> List[KhanDataHandling]:
        with open(self.file_path, encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            next(reader)  # Skip header

            duration = []
            video_data = []
            article_data = []
            exercise_data = []

            unit_number = 0
            recording = False
            unit_name = None
            lesson = None
            total_words = 0
            video_title_words = 0
            course_unit_lesson_words = 0
            exercises = 0
            articles = 0
            videos = 0
            total_seconds = 0
            title = "Arithmetic"
            stats_by_units = {}

            for line in reader:
                kind = line[0]
                original_title = line[1]
                course = line[5]

                if kind == "Course" and original_title == title:
                    course_unit_lesson_words += int(line[31])
                    recording = True

                if not recording:
                    continue

                if kind == "Course" and original_title != title:
                    break

                if kind == "Unit":
                    unit_number += 1
                    unit_name = f"Unit {unit_number}: {original_title}"
                    stats_by_units[unit_name] = 0
                    course_unit_lesson_words += int(line[31])

                if kind == "Lesson":
                    course_unit_lesson_words += int(line[31])
                    lesson = original_title

                if kind == "Article" and recording:
                    word_count = int(line[31])
                    total_words += word_count
                    test_link = f"https://preview--uk.khanacademy.org/devadmin/translations/edit/uk/{kind}/{line[2]}"
                    articles += 1
                    # print(f"{original_title}:{line[33]}")
                    article_data.append(KhanDataHandling(original_title, "None", course, unit_name, lesson, test_link, word_count))

                if kind == "Exercise" and recording:
                    word_count = int(line[31])
                    total_words += word_count
                    test_link = f"https://preview--uk.khanacademy.org/devadmin/translations/edit/uk/{kind}/{line[2]}"
                    exercises += 1
                    # print(f"{original_title}:{line[33]}")
                    exercise_data.append(KhanDataHandling(original_title, "None", course, unit_name, lesson, test_link, word_count))

                if kind == "Video" and recording:
                    youTube_link = f"https://www.youtube.com/watch?v={line[27]}"
                    video_title_words += int(line[31])
                    duration_in_seconds = int(line[17])
                    translated_title = line[26]
                    videos += 1
                    stats_by_units[unit_name] += duration_in_seconds
                    total_seconds += duration_in_seconds
                    duration = self.format_duration(duration_in_seconds)
                    video_data.append(
                        KhanDataHandling(original_title, translated_title, course, unit_name, lesson, youTube_link,
                                         duration))

            self.exporter(video_data, title)

            # Print stats
            print(f"{title} words: {total_words}")
            print(f"{video_title_words} words in video titles and descriptions")
            print(f"{course_unit_lesson_words} words in course/unit/lesson titles and descriptions")
            print(f"{videos} videos")
            print(f"{exercises} exercises")
            print(f"{articles} articles")

            return video_data

    def exporter(self, data: List[KhanDataHandling], file_to_output: str):
        output_path = os.path.join("C:/Users/lenovo/Documents/Khan data", f"{file_to_output}.csv")
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["", "Video title(En)", "Unit", "Lesson", "Duration", "Actor", "Recorded", "Auditor", "Validated", "Producer", "Postprocessed", "Who added?", "Added on platform", "Video title(Ua)", "Translator", "Name translated", "Link", "title"])
            for item in data:
                writer.writerow(["", "", self.escape_csv_field(item.unit_name), self.escape_csv_field(item.lesson_name), self.escape_csv_field(item.duration), "", "", "", "", "", "", "", "", "", "", "", self.escape_csv_field(item.youtube_link), self.escape_csv_field(item.original_title)])
        print(f"CSV file created successfully at {output_path}!")

    def exporter_titles(self, data: List[KhanDataHandling], file_to_output: str):
        output_path = os.path.join("C:/Users/lenovo/Documents/Khan data", f"{file_to_output}.csv")
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Video title(En)", "Translated title", "Unit", "Lesson"])
            for item in data:
                writer.writerow([self.escape_csv_field(item.original_title), self.escape_csv_field(item.translated_title), self.escape_csv_field(item.unit_name), self.escape_csv_field(item.lesson_name), self.escape_csv_field(item.duration)])
        print(f"CSV file created successfully at {output_path}!")

    @staticmethod
    def print_stats_by_units(stats: Dict[str, int]):
        for unit, total_seconds in stats.items():
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            duration = f"{hours:02}:{minutes:02}:{seconds:02}"
            print(f"{unit} video duration: {duration}")
