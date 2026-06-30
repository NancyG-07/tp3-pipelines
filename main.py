
import pipeline.getdataService
import pipeline.savedataService




def main():
    data= pipeline.getdataService.fetch_data(limit=200);
    pipeline.savedataService.saveData(data);


if __name__ == "__main__":
    main()