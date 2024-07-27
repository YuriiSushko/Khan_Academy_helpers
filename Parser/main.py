import extractor
import count_all_stats


def main(choice):
    if choice == 1:
        extractor_instance = extractor.ExtractAndExportToCsv("Parser/uk-export-recent.tsv")
        extractor_instance.extractor()
    else:
        all_stats_instance = count_all_stats.CountAllStats("Parser/uk-export-recent.tsv")
        all_stats_instance.extractor()


if __name__ == "__main__":
    main(1)
