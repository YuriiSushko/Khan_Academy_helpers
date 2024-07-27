import csv
from typing import Dict, Tuple
import os
from Parser.base_functions import BaseKhanDataHandling


class CountAllStats(BaseKhanDataHandling):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extractor(self):
        with open(self.file_path, encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            next(reader)  # Skip header

            duration = []
            unit_number = 0
            recording = False
            unit_name = None
            lesson = None
            total_words_exercise = 0
            total_words_article = 0
            total_words = 0
            exercises = 0
            articles = 0
            videos = 0
            total_seconds = 0
            course_title = "Early math review"
            stats_by_courses = {}
            stats_by_units = {}

            unique_videos = set()
            unique_exercises = set()
            unique_articles = set()

            video_repeats = {}
            exercise_repeats = {}
            article_repeats = {}

            for line in reader:
                kind = line[0]
                original_title = line[1]
                course = line[5]

                if kind == "Domain" and original_title == "Math":
                    recording = True

                if not recording:
                    continue

                if kind == "Domain" and original_title != "Math":
                    break

                if kind == "Course":
                    total_time = self.format_duration(total_seconds)
                    stats_by_courses[course_title] = (unit_number, exercises, articles, videos, total_words_article, total_words_exercise, total_time)

                    if course_title != original_title:
                        unit_number = 0
                        total_seconds = 0
                        total_words_exercise = 0
                        total_words_article = 0
                        exercises = 0
                        articles = 0
                        videos = 0
                        total_words = 0

                    course_title = original_title

                if kind == "Unit":
                    unit_number += 1
                    unit_name = f"Unit {unit_number}: {original_title}"
                    stats_by_units[unit_name] = 0

                if kind == "Lesson":
                    lesson = original_title

                if kind == "Exercise" and recording:
                    if original_title not in unique_exercises:
                        word_count = int(line[31])
                        total_words_exercise += word_count
                        exercises += 1
                        total_words += word_count
                        unique_exercises.add(original_title)
                        exercise_repeats[original_title] = 1
                    else:
                        exercise_repeats[original_title] += 1

                if kind == "Article" and recording:
                    if original_title not in unique_articles:
                        word_count = int(line[31])
                        total_words_article += word_count
                        articles += 1
                        total_words += word_count
                        unique_articles.add(original_title)
                        article_repeats[original_title] = 1
                    else:
                        article_repeats[original_title] += 1

                if kind == "Video" and recording:
                    if original_title not in unique_videos:
                        duration_in_seconds = int(line[17])
                        videos += 1
                        if unit_name:
                            stats_by_units[unit_name] += duration_in_seconds
                        total_seconds += duration_in_seconds
                        unique_videos.add(original_title)
                        video_repeats[original_title] = 1
                    else:
                        video_repeats[original_title] += 1

            total_time_for_last_course = self.format_duration(total_seconds)
            stats_by_courses[course_title] = (unit_number, exercises, articles, videos, total_words_article, total_words_exercise, total_time_for_last_course)

            self.exporter(stats_by_courses, "Math")

    def exporter(self, stats: Dict[str, Tuple[int, int, int, int, int, int, str]], course: str):
        output_path = os.path.join("C:/Users/lenovo/Documents/Khan data", f"{course}.csv")
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["", "Units", "Exercises", "Articles", "Videos", "Words Articles", "Words Exercises", "Duration"])
            for key, value in stats.items():
                writer.writerow([self.escape_csv_field(key), value[0], value[1], value[2], value[3], value[4], value[5], value[6]])
        print(f"CSV file created successfully at {output_path}!")
