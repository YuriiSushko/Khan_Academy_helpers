class BaseKhanDataHandling:
    @staticmethod
    def format_duration(total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    @staticmethod
    def escape_csv_field(field):
        if any(c in field for c in [',', '"', '\n']):
            field = field.replace('"', '""')
            return f'"{field}"'
        return field


class KhanDataHandling:
    def __init__(self, original_title: str, translated_title: str, course_name: str, unit_name: str, lesson_name: str, youtube_link: str, duration: str):
        self.original_title = original_title
        self.translated_title = translated_title
        self.course_name = course_name
        self.unit_name = unit_name
        self.lesson_name = lesson_name
        self.youtube_link = youtube_link
        self.duration = duration