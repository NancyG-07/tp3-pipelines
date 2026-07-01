
import pipeline.getdataService
import pipeline.savedataService


import argparse
import time


def main():


    parser = argparse.ArgumentParser()

    parser.add_argument("--schedule", action="store_true")
    parser.add_argument("--interval", type=float, default=1)

    args = parser.parse_args()

    if args.schedule:
        print(f"Mode planifié aux {args.interval} heure(s)")

        while True:
            print("Exécution du pipeline...")
            data= pipeline.getdataService.fetch_data(limit=200);
            pipeline.savedataService.saveData(data);           

            time.sleep(args.interval * 3600)

    else:
        print("Exécution unique")
        # run_pipeline()









if __name__ == "__main__":
    main()